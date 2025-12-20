# Walkthrough: Plataforma Pedagógica CID

Este documento detalla las nuevas herramientas integradas en el sistema CID para permitir a los doctores en educación diseñar rutas de aprendizaje con rigor pedagógico.

## 1. Modelado de Ontologías y Competencias
Se han implementado modelos de datos avanzados en `functions/common/pedagogical_models.py` que permiten definir:
- **Taxonomías:** Marcos de referencia como Bloom o DIGCOMP.
- **Competencias:** Habilidades específicas vinculadas a niveles (Principiante, Intermedio, Experto).
- **Mapeo de Evidencias:** Conexión entre actividades de Moodle y objetivos pedagógicos.

## 2. Motor de Inferencia de Metadatos (IA Asistida)
La nueva Cloud Function `analyze_syllabus` simula un motor de IA que:
- Lee el contenido de un curso de Moodle (vía `MoodleClient`).
- Sugiere metadatos bajo estándares **IEEE LOM** y **Dublin Core**.
- Clasifica automáticamente el nivel de dificultad y genera etiquetas clave.

## 3. Orquestador de Reglas de Avance (Lógica Booleana)
El motor de validación ha sido actualizado (`functions/common/rule_evaluator.py`) para soportar:
- Operadores lógicos: **AND, OR, NOT**.
- Condiciones complejas: Comparación de puntajes y atributos del alumno (ej. "Si score > 90 Y es Becado").
- Integración con el **SIS Connector** para filtrar rutas basadas en datos del sistema escolar.

## 4. Simulador de Rutas (Modo "Estudiante Fantasma")
La Cloud Function `simulate_path` permite a los doctores:
- Probar una ruta de aprendizaje completa antes de publicarla.
- Simular resultados de exámenes y atributos de perfil.
- Verificar qué nodos se desbloquean y qué insignias se emiten.

## 5. LTI Wrapper y Deep Linking
Se ha integrado el `LTIHandler` (`functions/common/lti_handler.py`) que permite:
- **Lanzamiento Seguro:** Generación de URLs firmadas para ver contenido de Moodle sin salir de la plataforma.
- **Curaduría Directa:** Exploración de recursos de Moodle (quizzes, foros) para vincularlos a nodos de la ruta.

## 6. SIS Connector Avanzado
El `SISClient` (`functions/common/sis_client.py`) permite:
- **Perfilado Académico:** Acceso a datos de edad, grado, promedio y estatus de beca.
- **Segmentación Pedagógica:** Filtrado de alumnos para rutas personalizadas basadas en criterios del sistema escolar.

## 7. Cumplimiento con Open Badges 3.0
El sistema de emisión ahora soporta metadatos avanzados:
- **Alineaciones:** Vinculación de la insignia con estándares externos o marcos de competencias.
- **Evidencias Narrativas:** El `EvidenceVerifier` genera justificaciones pedagógicas automáticas basadas en el desempeño en Moodle.

---

### Cómo empezar
1. **Inicializar datos de prueba:**
   ```bash
   python scripts/init_pedagogical_data.py
   ```
2. **Probar análisis de sílabo:**
   ```bash
   curl -X POST http://localhost:8080/analyze_syllabus -d '{"course_id": "MATH101"}'
   ```
3. **Simular una ruta:**
   ```bash
   curl -X POST http://localhost:8080/simulate_path -d '{"path_id": "path-math-excellence", "mock_scores": {"MATH101": 95}}'
   ```
4. **Verificar cumplimiento OB 3.0:**
   Revisar los logs de `call_acreditta` para ver cómo se mapean las alineaciones y evidencias.
