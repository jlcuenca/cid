# CCA - Conector de Credenciales Automático

Sistema serverless en GCP para la emisión automatizada de insignias digitales (Acreditta) en el ecosistema de una institución educativa.

## 🏗️ Arquitectura

```
Moodle Webhook → Pub/Sub → Cloud Workflow → Cloud Functions → Acreditta/SIS
                                ↓
                           Firestore (Rules + Audit)
```

### Componentes

- **Cloud Pub/Sub**: Punto de entrada para eventos de Moodle
- **Cloud Workflows**: Orquestación del flujo VALIDAR → EMITIR → NOTIFICAR
- **Cloud Functions** (3):
  - `validate_rule`: Valida reglas de emisión desde Firestore
  - `call_acreditta`: Emite insignias via API de Acreditta
  - `update_sis`: Actualiza SIS y registra auditoría
- **Firestore**: Base de datos serverless para reglas y logs
- **Secret Manager**: Almacenamiento seguro de credenciales

## 📋 Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://www.terraform.io/downloads) >= 1.0
- Python 3.11+
- Cuenta de GCP con permisos de administrador
- Credenciales de Acreditta API

## 🚀 Deployment

### 1. Configurar GCP Project

```bash
# Autenticar con GCP
gcloud auth login
gcloud auth application-default login

# Configurar proyecto
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
```

### 2. Configurar Variables de Terraform

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
```

Editar `terraform.tfvars` con tus valores:
```hcl
project_id = "your-gcp-project-id"
region     = "us-central1"
environment = "dev"
acreditta_api_url = "https://api.acreditta.com/v1"
sis_db_host = "your-sis-host.example.com"
```

### 3. Desplegar Infraestructura

```bash
# Inicializar Terraform
terraform init

# Revisar plan de despliegue
terraform plan

# Aplicar cambios
terraform apply
```

### 4. Configurar Secrets

Después del despliegue, actualizar los secrets con credenciales reales:

```bash
# Acreditta API Key
echo -n "YOUR_ACREDITTA_API_KEY" | gcloud secrets versions add acreditta-api-key --data-file=-

# SIS Database User
echo -n "YOUR_SIS_DB_USER" | gcloud secrets versions add sis-db-user --data-file=-

# SIS Database Password
echo -n "YOUR_SIS_DB_PASS" | gcloud secrets versions add sis-db-pass --data-file=-
```

### 5. Inicializar Firestore

Crear las colecciones necesarias en Firestore:

```bash
# Crear colección de reglas (ejemplo)
gcloud firestore documents create --collection=reglas_emision --document-id=rule-001 \
  --data='{"course_id":"MATH101","evaluation_id":"final_exam","min_score":80,"badge_template_id":"excellence-badge","badge_title":"Excellence in Mathematics","active":true}'
```

### 6. Configurar Moodle Webhook

Configurar Moodle para publicar eventos al tópico Pub/Sub:

- **Topic**: `moodle-evaluation-events`
- **Project**: Tu GCP Project ID
- **Formato**: JSON con campos: `student_id`, `course_id`, `evaluation_id`, `score`, `timestamp`

## 🧪 Testing

### Test Local de Funciones

```bash
# Instalar dependencias
pip install -r requirements.txt

# Test validate_rule
cd functions/validate_rule
functions-framework --target=validate_rule --debug

# En otra terminal
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "12345",
    "course_id": "MATH101",
    "evaluation_id": "final_exam",
    "score": 85,
    "timestamp": "2025-12-03T12:00:00Z"
  }'
```

### Test de Workflow Completo

```bash
# Ejecutar workflow manualmente
gcloud workflows execute cca-badge-issue-flow \
  --location=us-central1 \
  --data='{
    "data": {
      "student_id": "12345",
      "course_id": "MATH101",
      "evaluation_id": "final_exam",
      "score": 85,
      "timestamp": "2025-12-03T12:00:00Z"
    }
  }'

# Ver ejecuciones
gcloud workflows executions list cca-badge-issue-flow --location=us-central1

# Ver detalles de una ejecución
gcloud workflows executions describe EXECUTION_ID \
  --workflow=cca-badge-issue-flow \
  --location=us-central1
```

### Test de Pub/Sub

```bash
# Publicar mensaje de prueba
gcloud pubsub topics publish moodle-evaluation-events \
  --message='{
    "student_id": "12345",
    "course_id": "MATH101",
    "evaluation_id": "final_exam",
    "score": 85,
    "timestamp": "2025-12-03T12:00:00Z"
  }'
```

## 📊 Monitoring

### Ver Logs

```bash
# Logs de Cloud Functions
gcloud functions logs read cca-validate-rule --region=us-central1
gcloud functions logs read cca-call-acreditta --region=us-central1
gcloud functions logs read cca-update-sis --region=us-central1

# Logs de Workflow
gcloud logging read "resource.type=workflows.googleapis.com/Workflow" --limit=50
```

### Métricas en Cloud Console

- [Cloud Functions Metrics](https://console.cloud.google.com/functions)
- [Workflows Executions](https://console.cloud.google.com/workflows)
- [Pub/Sub Monitoring](https://console.cloud.google.com/cloudpubsub)

## 📁 Project Structure

```
cid/
├── infrastructure/
│   └── terraform/
│       ├── main.tf              # Recursos principales de GCP
│       ├── variables.tf         # Variables de configuración
│       ├── outputs.tf           # Outputs del despliegue
│       ├── workflow.yaml        # Definición del workflow
│       └── terraform.tfvars.example
├── functions/
│   ├── common/                  # Módulos compartidos
│   │   ├── __init__.py
│   │   ├── config.py           # Configuración y secrets
│   │   ├── models.py           # Modelos Pydantic
│   │   └── database.py         # Cliente Firestore
│   ├── validate_rule/
│   │   ├── main.py             # Cloud Function
│   │   └── requirements.txt
│   ├── call_acreditta/
│   │   ├── main.py             # Cloud Function
│   │   ├── acreditta_handler.py # Cliente API Acreditta
│   │   └── requirements.txt
│   └── update_sis/
│       ├── main.py             # Cloud Function
│       ├── sis_connector.py    # Conector SIS legacy
│       └── requirements.txt
├── docs/
│   └── api-contracts.md        # Contratos de API
├── requirements.txt            # Dependencias globales
├── .env.example               # Template de variables
└── README.md
```

## 🔒 Security

- **Secrets**: Todas las credenciales en Secret Manager
- **IAM**: Principio de menor privilegio para service accounts
- **VPC**: Considerar VPC Service Controls para producción
- **Audit**: Todos los eventos registrados en Firestore

## 🔧 Troubleshooting

### Error: "Permission denied"

Verificar IAM roles:
```bash
gcloud projects get-iam-policy $GCP_PROJECT_ID
```

### Error: "Secret not found"

Verificar que los secrets existan:
```bash
gcloud secrets list
gcloud secrets versions access latest --secret=acreditta-api-key
```

### Workflow falla en paso de validación

Revisar logs y verificar reglas en Firestore:
```bash
gcloud firestore documents list --collection=reglas_emision
```

## 📚 Documentation

- [API Contracts](docs/api-contracts.md)
- [Cloud Workflows Documentation](https://cloud.google.com/workflows/docs)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)

## 🤝 Contributing

1. Fork el repositorio
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 License

MIT License - ver archivo LICENSE para detalles

## 👥 Support

Para soporte, contactar al equipo de desarrollo o abrir un issue en GitHub.
