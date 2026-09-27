import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "shared/api/client";
import type { PaginatedResponse } from "shared/api/types";

export type ReportSnapshot = Record<string, unknown>;

export type Report = {
  id: string;
  project: string;
  project_id?: string;
  project_display?: string;
  object_name?: string;
  title: string;
  version: number;
  status: string;
  summary: string;
  generated_at?: string | null;
  approved_at?: string | null;
  preview_available?: boolean;
  json_snapshot?: ReportSnapshot;
  download_docx_url?: string | null;
  download_pdf_url?: string | null;
};

export const PDF_EXPORT_AVAILABLE = false;
export const PDF_EXPORT_UNAVAILABLE_MESSAGE =
  "PDF export is temporarily unavailable. Use DOCX export while the PDF renderer is being upgraded for Cyrillic support.";

export type ReportTemplateBlock = {
  id: string;
  template: string;
  block_type: string;
  block_type_display?: string;
  title_override: string;
  sort_order: number;
  is_enabled: boolean;
  is_required: boolean;
  settings: Record<string, unknown>;
};

export type ReportTemplate = {
  id: string;
  code: string;
  name: string;
  description: string;
  is_active: boolean;
  is_default: boolean;
  blocks: ReportTemplateBlock[];
};

type ReportFileOptions = {
  openInNewTab?: boolean;
  download?: boolean;
  fallbackFilename: string;
};

function normalizeReportFileUrl(url: string) {
  try {
    const absoluteUrl = new URL(url);
    return `${absoluteUrl.pathname}${absoluteUrl.search}`;
  } catch {
    if (url.startsWith("/api/")) {
      return url.slice(4);
    }
    if (url.startsWith("api/")) {
      return `/${url.slice(4)}`;
    }
    return url.startsWith("/") ? url : `/${url}`;
  }
}

function extractFilename(contentDisposition: string | undefined, fallbackFilename: string) {
  if (!contentDisposition) {
    return fallbackFilename;
  }

  const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    return decodeURIComponent(utf8Match[1]);
  }

  const quotedMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
  if (quotedMatch?.[1]) {
    return quotedMatch[1];
  }

  return fallbackFilename;
}

async function fetchReportFile(url: string, fallbackFilename: string) {
  const { data, headers } = await apiClient.get<Blob>(normalizeReportFileUrl(url), {
    responseType: "blob",
  });

  const filename = extractFilename(headers["content-disposition"] as string | undefined, fallbackFilename);
  return { blob: data, filename };
}

async function accessReportFile(url: string | null | undefined, options: ReportFileOptions) {
  if (!url) {
    return;
  }

  const previewWindow = options.openInNewTab ? window.open("", "_blank") : null;

  try {
    const { blob, filename } = await fetchReportFile(url, options.fallbackFilename);
    const blobUrl = URL.createObjectURL(blob);

    if (options.download) {
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.append(link);
      link.click();
      link.remove();
    }

    if (options.openInNewTab) {
      if (previewWindow) {
        previewWindow.location.href = blobUrl;
      } else {
        window.open(blobUrl, "_blank");
      }
    }

    window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
  } catch (error) {
    previewWindow?.close();
    throw error;
  }
}

export async function downloadReportDocx(url: string | null | undefined) {
  await accessReportFile(url, {
    openInNewTab: true,
    download: true,
    fallbackFilename: "technical-report.docx",
  });
}

export async function openReportPdf(url: string | null | undefined) {
  await accessReportFile(url, {
    openInNewTab: true,
    download: false,
    fallbackFilename: "technical-report.pdf",
  });
}

async function fetchReports() {
  const { data } = await apiClient.get<PaginatedResponse<Report>>("/reports/");
  return data;
}

async function fetchReportTemplates() {
  const { data } = await apiClient.get<PaginatedResponse<ReportTemplate>>("/report-templates/");
  return data;
}

async function createReportTemplate(payload: Pick<ReportTemplate, "code" | "name" | "description" | "is_active" | "is_default">) {
  const { data } = await apiClient.post<ReportTemplate>("/report-templates/", payload);
  return data;
}

async function updateReportTemplate(payload: Partial<ReportTemplate> & { id: string }) {
  const { id, ...body } = payload;
  const { data } = await apiClient.patch<ReportTemplate>(`/report-templates/${id}/`, body);
  return data;
}

async function updateReportTemplateBlock(payload: Partial<ReportTemplateBlock> & { id: string }) {
  const { id, ...body } = payload;
  const { data } = await apiClient.patch<ReportTemplateBlock>(`/report-template-blocks/${id}/`, body);
  return data;
}

async function fetchProjectReports(projectId: string) {
  const { data } = await apiClient.get<Report[]>(`/projects/${projectId}/reports/`);
  return data;
}

async function fetchReport(reportId: string) {
  const { data } = await apiClient.get<Report>(`/reports/${reportId}/`);
  return data;
}

async function generateProjectReport(projectId: string, fileFormat: "docx" | "pdf") {
  const { data } = await apiClient.post<Report>(`/projects/${projectId}/reports/generate/`, {
    file_format: fileFormat,
  });
  return data;
}

async function generateProjectDocx(projectId: string) {
  return generateProjectReport(projectId, "docx");
}

async function generateProjectPdf(projectId: string) {
  return generateProjectReport(projectId, "pdf");
}

async function approveReport(reportId: string) {
  const { data } = await apiClient.post<Report>(`/reports/${reportId}/approve/`);
  return data;
}

export function useReportsQuery() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: fetchReports,
  });
}

export function useReportTemplatesQuery() {
  return useQuery({
    queryKey: ["report-templates"],
    queryFn: fetchReportTemplates,
  });
}

export function useProjectReportsQuery(projectId: string) {
  return useQuery({
    queryKey: ["project-reports", projectId],
    queryFn: () => fetchProjectReports(projectId),
    enabled: Boolean(projectId),
  });
}

export function useReportQuery(reportId: string) {
  return useQuery({
    queryKey: ["reports", reportId],
    queryFn: () => fetchReport(reportId),
    enabled: Boolean(reportId),
  });
}

export function useGenerateProjectDocxMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => generateProjectDocx(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["project-reports", projectId] });
    },
  });
}

export function useGenerateProjectPdfMutation(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => generateProjectPdf(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["project-reports", projectId] });
    },
  });
}

export function useApproveReportMutation(projectId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: approveReport,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["reports", data.id] });
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ["project-reports", projectId] });
      }
    },
  });
}

export function useCreateReportTemplateMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createReportTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["report-templates"] });
    },
  });
}

export function useUpdateReportTemplateMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateReportTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["report-templates"] });
    },
  });
}

export function useUpdateReportTemplateBlockMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateReportTemplateBlock,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["report-templates"] });
    },
  });
}
