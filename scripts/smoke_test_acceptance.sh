#!/usr/bin/env bash
set -euo pipefail

BASE=http://localhost:8000/api
TMP_DIR=$(mktemp -d)
PHOTO_FILE="$TMP_DIR/demo-photo.jpg"
printf "demo image bytes" > "$PHOTO_FILE"

json_get() {
  python3 -c 'import json,sys
data=json.load(sys.stdin)
for key in sys.argv[1].split("."):
    data = data[int(key)] if key.isdigit() else data[key]
print(data)' "$1"
}

login() {
  local email=$1
  local password=$2
  curl -s -X POST "$BASE/auth/login/" -H "Content-Type: application/json" -d "{\"email\":\"$email\",\"password\":\"$password\"}"
}

MANAGER_JSON=$(login manager@example.com Password123!)
ENGINEER_JSON=$(login engineer@example.com Password123!)
EXPERT_JSON=$(login expert@example.com Password123!)
MANAGER_TOKEN=$(printf "%s" "$MANAGER_JSON" | json_get access)
ENGINEER_TOKEN=$(printf "%s" "$ENGINEER_JSON" | json_get access)
EXPERT_TOKEN=$(printf "%s" "$EXPERT_JSON" | json_get access)

OBJECT_JSON=$(curl -s -X POST "$BASE/objects/" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acceptance Industrial Building","address":"г. Екатеринбург, ул. Тестовая, 10","object_type":"Производственное здание","purpose":"Промышленный корпус","construction_year":2019,"floors_count":2,"area":"2400.0"}')
OBJECT_ID=$(printf "%s" "$OBJECT_JSON" | json_get id)

PROJECT_JSON=$(curl -s -X POST "$BASE/projects/" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"building_object\":\"$OBJECT_ID\",\"customer_name\":\"Acceptance Customer\",\"contract_number\":\"ACC-2026-001\",\"inspection_reason\":\"Комплексное обследование перед ремонтом\",\"inspection_goal\":\"Проверка полного маршрута формирования отчёта\",\"inspection_type\":\"Комплексное обследование\",\"start_date\":\"2026-05-24\",\"end_date\":\"2026-05-31\"}")
PROJECT_ID=$(printf "%s" "$PROJECT_JSON" | json_get id)

curl -s -X PATCH "$BASE/projects/$PROJECT_ID/" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"In Progress","final_condition_category":"Ограниченно-работоспособное"}' >/dev/null

curl -s -X POST "$BASE/technical-tasks/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project\":\"$PROJECT_ID\",\"execution_basis\":\"Договор ACC-2026-001\",\"survey_goal\":\"Комплексное обследование промышленного здания\",\"building_parts\":\"Фундаменты, колонны\",\"engineering_systems\":\"Электроснабжение\",\"required_methods\":\"Визуальное обследование, инструментальное измерение\",\"result_requirements\":\"Паспорт здания, DOCX, PDF\",\"deadlines\":\"31.05.2026\",\"output_documentation\":\"DOCX, PDF, приложения\"}" >/dev/null

curl -s -X POST "$BASE/work-programs/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project\":\"$PROJECT_ID\",\"structures\":\"Фундаменты и колонны\",\"zones\":\"Подвал и 1 этаж\",\"methods\":\"Визуальное обследование, фотофиксация, инструментальное измерение\",\"tools_and_devices\":\"Рулетка, трещиномер\",\"measurements\":\"Ширина раскрытия трещин\",\"photo_requirements\":\"Обзорное фото фундамента и фото дефекта колонны\",\"responsible_executors\":\"Инженер, эксперт\",\"completeness_checklist\":[\"Элементы созданы\",\"Фото загружены\",\"Замеры внесены\"]}" >/dev/null

curl -s -X POST "$BASE/files/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -F "file=@$PHOTO_FILE" \
  -F "category=project" \
  -F "appendix_type=technical_task" \
  -F "project=$PROJECT_ID" \
  -F "building_object=$OBJECT_ID" \
  -F "caption=Техническое задание" \
  -F "is_for_report=true" >/dev/null

curl -s -X POST "$BASE/files/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -F "file=@$PHOTO_FILE" \
  -F "category=project" \
  -F "appendix_type=work_program" \
  -F "project=$PROJECT_ID" \
  -F "building_object=$OBJECT_ID" \
  -F "caption=Программа работ" \
  -F "is_for_report=true" >/dev/null

curl -s -X POST "$BASE/files/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -F "file=@$PHOTO_FILE" \
  -F "category=project" \
  -F "appendix_type=calculation" \
  -F "project=$PROJECT_ID" \
  -F "building_object=$OBJECT_ID" \
  -F "caption=Поверочные расчеты" \
  -F "is_for_report=true" >/dev/null

TYPES=("Фундаменты" "Колонны")
DEFECTIVE_ELEMENT_ID=""
NO_DEFECT_ELEMENT_ID=""
INDEX=0
for TYPE in "${TYPES[@]}"; do
  INDEX=$((INDEX + 1))
  HAS_DEFECTS=false
  NO_COMMENT='Видимых дефектов и повреждений не выявлено'
  CATEGORY='Работоспособное'
  CONCLUSION='Эксплуатация возможна'
  RECOMMENDATION='not_required'
  if [ "$TYPE" = "Колонны" ]; then
    HAS_DEFECTS=true
    NO_COMMENT=''
    CATEGORY='Ограниченно-работоспособное'
    CONCLUSION='Требуется локальный ремонт и наблюдение'
    RECOMMENDATION='repair'
  fi

  ELEMENT_JSON=$(curl -s -X POST "$BASE/elements/" \
    -H "Authorization: Bearer $ENGINEER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"project\":\"$PROJECT_ID\",\"building_object\":\"$OBJECT_ID\",\"element_type\":\"$TYPE\",\"name\":\"$TYPE\",\"location\":\"Зона $INDEX\",\"floor\":\"$INDEX этаж\",\"material\":\"Монолитный железобетон\",\"inspection_method\":\"Визуальное обследование\",\"visual_condition\":\"удовлетворительное\",\"has_defects\":$HAS_DEFECTS,\"no_defects_comment\":\"$NO_COMMENT\",\"condition_category\":\"$CATEGORY\",\"conclusion\":\"$CONCLUSION\",\"recommendation\":\"$RECOMMENDATION\"}")
  ELEMENT_ID=$(printf "%s" "$ELEMENT_JSON" | json_get id)

  if [ "$HAS_DEFECTS" = true ]; then
    DEFECTIVE_ELEMENT_ID=$ELEMENT_ID
  else
    if [ -z "$NO_DEFECT_ELEMENT_ID" ]; then
      NO_DEFECT_ELEMENT_ID=$ELEMENT_ID
    fi
    curl -s -X POST "$BASE/files/" \
      -H "Authorization: Bearer $ENGINEER_TOKEN" \
      -F "file=@$PHOTO_FILE" \
      -F "category=element" \
      -F "project=$PROJECT_ID" \
      -F "building_object=$OBJECT_ID" \
      -F "structural_element=$ELEMENT_ID" \
      -F "caption=Обзорное фото $TYPE" \
      -F "is_for_report=true" >/dev/null
  fi
done

DEFECT_JSON=$(curl -s -X POST "$BASE/defects/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project\":\"$PROJECT_ID\",\"building_object\":\"$OBJECT_ID\",\"structural_element\":\"$DEFECTIVE_ELEMENT_ID\",\"defect_type\":\"Трещина\",\"title\":\"Трещина в колонне\",\"description\":\"Выявлена трещина в защитном слое колонны\",\"location\":\"1 этаж\",\"floor\":\"1 этаж\",\"severity\":\"Умеренный\",\"probable_cause\":\"Усадочные процессы\",\"preliminary_condition_category\":\"Ограниченно-работоспособное\",\"final_condition_category\":\"Ограниченно-работоспособное\",\"recommendation\":\"Требуется наблюдение в динамике\",\"status\":\"Confirmed\"}")
DEFECT_ID=$(printf "%s" "$DEFECT_JSON" | json_get id)

curl -s -X POST "$BASE/files/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -F "file=@$PHOTO_FILE" \
  -F "category=defect" \
  -F "project=$PROJECT_ID" \
  -F "building_object=$OBJECT_ID" \
  -F "structural_element=$DEFECTIVE_ELEMENT_ID" \
  -F "defect=$DEFECT_ID" \
  -F "caption=Фото дефекта" \
  -F "is_for_report=true" >/dev/null

MEASUREMENT_JSON=$(curl -s -X POST "$BASE/measurements/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project\":\"$PROJECT_ID\",\"structural_element\":\"$DEFECTIVE_ELEMENT_ID\",\"defect\":\"$DEFECT_ID\",\"measurement_type\":\"Ширина раскрытия трещины\",\"value\":\"0.4\",\"unit\":\"мм\",\"location\":\"1 этаж\",\"measured_at\":\"2026-05-24T10:00:00+05:00\",\"method\":\"Инструментальное измерение\",\"device\":\"Трещиномер\",\"comment\":\"Тестовый замер раскрытия трещины\"}")
MEASUREMENT_ID=$(printf "%s" "$MEASUREMENT_JSON" | json_get id)

curl -s -X POST "$BASE/files/" \
  -H "Authorization: Bearer $ENGINEER_TOKEN" \
  -F "file=@$PHOTO_FILE" \
  -F "category=measurement" \
  -F "project=$PROJECT_ID" \
  -F "building_object=$OBJECT_ID" \
  -F "structural_element=$DEFECTIVE_ELEMENT_ID" \
  -F "measurement=$MEASUREMENT_ID" \
  -F "caption=Фото замера" \
  -F "is_for_report=true" >/dev/null

SUBMIT_JSON=$(curl -s -X POST "$BASE/projects/$PROJECT_ID/submit_review/" -H "Authorization: Bearer $ENGINEER_TOKEN")
APPROVE_PROJECT_JSON=$(curl -s -X POST "$BASE/projects/$PROJECT_ID/approve/" -H "Authorization: Bearer $EXPERT_TOKEN")
DOCX_JSON=$(curl -s -X POST "$BASE/projects/$PROJECT_ID/reports/generate/" -H "Authorization: Bearer $ENGINEER_TOKEN" -H "Content-Type: application/json" -d '{"file_format":"docx"}')
PDF_JSON=$(curl -s -X POST "$BASE/projects/$PROJECT_ID/reports/generate/" -H "Authorization: Bearer $ENGINEER_TOKEN" -H "Content-Type: application/json" -d '{"file_format":"pdf"}')
REPORT_ID=$(printf "%s" "$PDF_JSON" | json_get id)
APPROVE_REPORT_JSON=$(curl -s -X POST "$BASE/reports/$REPORT_ID/approve/" -H "Authorization: Bearer $EXPERT_TOKEN")

DOCX_DOWNLOAD="$TMP_DIR/report.docx"
PDF_DOWNLOAD="$TMP_DIR/report.pdf"
curl -s "$BASE/reports/$REPORT_ID/download-docx/" -H "Authorization: Bearer $ENGINEER_TOKEN" -o "$DOCX_DOWNLOAD"
curl -s "$BASE/reports/$REPORT_ID/download-pdf/" -H "Authorization: Bearer $ENGINEER_TOKEN" -o "$PDF_DOWNLOAD"

DOC_XML=$(unzip -p "$DOCX_DOWNLOAD" word/document.xml)
printf "%s" "$DOC_XML" | grep -q "ТЕХНИЧЕСКИЙ ОТЧЕТ"
printf "%s" "$DOC_XML" | grep -q "Acceptance Industrial Building"
printf "%s" "$DOC_XML" | grep -q "5. РЕЗУЛЬТАТЫ ПОВЕРОЧНЫХ РАСЧЕТОВ"
printf "%s" "$DOC_XML" | grep -q "Фундаменты"
printf "%s" "$DOC_XML" | grep -q "Колонны"
printf "%s" "$DOC_XML" | grep -q "Трещина в колонне"
printf "%s" "$DOC_XML" | grep -q "0.4 мм"

printf "OBJECT_ID=%s\nPROJECT_ID=%s\nNO_DEFECT_ELEMENT_ID=%s\nDEFECTIVE_ELEMENT_ID=%s\nDEFECT_ID=%s\nMEASUREMENT_ID=%s\nREPORT_ID=%s\nSUBMIT_STATUS=%s\nPROJECT_APPROVE_STATUS=%s\nREPORT_APPROVE_STATUS=%s\nDOCX_SIZE=%s\nPDF_SIZE=%s\nVERIFIED_REPORT_CONTENT=ok\n" \
  "$OBJECT_ID" "$PROJECT_ID" "$NO_DEFECT_ELEMENT_ID" "$DEFECTIVE_ELEMENT_ID" "$DEFECT_ID" "$MEASUREMENT_ID" "$REPORT_ID" \
  "$(printf "%s" "$SUBMIT_JSON" | json_get status)" \
  "$(printf "%s" "$APPROVE_PROJECT_JSON" | json_get status)" \
  "$(printf "%s" "$APPROVE_REPORT_JSON" | json_get status)" \
  "$(wc -c < "$DOCX_DOWNLOAD")" "$(wc -c < "$PDF_DOWNLOAD")"
