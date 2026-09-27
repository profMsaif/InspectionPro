export type MeResponse = {
  id: string;
  email: string;
  full_name: string;
  role: "Admin" | "Manager" | "Engineer" | "Expert" | "Client";
  organization: string;
  is_active: boolean;
};

