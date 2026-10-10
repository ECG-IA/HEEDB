# Variantes de arritmias cardíacas en HEEDB — por variante y hospital

**Archivo:** `informe_viabilidad_HEEDB.md` (reemplaza versión anterior).
**Corte y conteo verificado:** 10 oct 2026 contra archivos locales `metadatos/MGH` (= ECG/I0001) y `metadatos/Emory` (= ECG/I0006).
**Fuentes etiqueta:** `diagnoses_dictionary.csv` (503 códigos, idéntico en ambos), `diagnoses_v24.csv` (reproceso 12SL v24), `diagnoses_acquisition.csv` columna `codes_physician` (overread médico).
**Lectura conteos:** cada cifra = nº de ECGs cuya lista contiene ese código (un ECG suma en varios códigos). `0` = etiqueta existe en diccionario pero sin casos en esa fuente/hospital. Universos: MGH v24 10,471,531 / physician 8,608,018 con etiqueta; Emory v24 974,172 / physician 998,168 con etiqueta.

## 1. Ritmo sinusal (control y frecuencia)

Motor base del ECG. `NSR` = ritmo normal (control). `SBRAD/MSBRAD` = lento. `STACH` = rápido. `LHR/PR-SBRAD` = flags de verificar.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 22 | NSR | normal sinus rhythm | 4,115,214 | 4,456,804 |
| 19 | SRTH | sinus rhythm | 1,796,277 | 1,436,258 |
| 21 | SBRAD | sinus bradycardia | 1,138,840 | 987,640 |
| 23 | STACH | sinus tachycardia | 902,408 | 803,557 |
| 24 | MSBRAD | marked sinus bradycardia | 51,719 | 105,197 |
| 265 | PR-SBRAD | probable sinus bradycardia, verify av conduction | 0 | 6,544 |
| 287 | LHR | low heart rate, verify av conduction | 0 | 201,085 |

### I0006 — Emory (EUH)

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 22 | NSR | normal sinus rhythm | 493,537 | 481,449 |
| 19 | SRTH | sinus rhythm | 120,391 | 175,192 |
| 21 | SBRAD | sinus bradycardia | 141,581 | 135,308 |
| 23 | STACH | sinus tachycardia | 76,273 | 76,132 |
| 24 | MSBRAD | marked sinus bradycardia | 5,723 | 17,695 |
| 265 | PR-SBRAD | probable sinus bradycardia, verify av conduction | 0 | 87 |
| 287 | LHR | low heart rate, verify av conduction | 0 | 28 |

## 2. Arritmia sinusal

Irregularidad ligada a respiración. No es fibrilación.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 251 | SAR | with sinus arrhythmia | 333,597 | 334,170 |
| 252 | MSAR | with marked sinus arrhythmia | 106,660 | 207,799 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 251 | SAR | with sinus arrhythmia | 40,186 | 47,222 |
| 252 | MSAR | with marked sinus arrhythmia | 11,059 | 17,443 |

## 3. Fibrilación auricular (AFIB)

La arritmia sostenida más prevalente del dataset. `RVR/SVR` = modificadores (respuesta ventricular rápida/lenta, casi siempre acompañan a AFIB). `ABER` = con aberrancia.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 161 | AFIB | atrial fibrillation | 767,742 | 929,074 |
| 171 | RVR | with rapid ventricular response | 252,983 | 298,149 |
| 172 | SVR | with slow ventricular response | 58,402 | 145,241 |
| 181 | ABER | with premature ventricular or aberrantly conducted complexes | 243,873 | 129,812 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 161 | AFIB | atrial fibrillation | 60,133 | 88,364 |
| 171 | RVR | with rapid ventricular response | 19,440 | 18,753 |
| 172 | SVR | with slow ventricular response | 4,492 | 4,610 |
| 181 | ABER | with premature ventricular or aberrantly conducted complexes | 13,821 | 12,321 |

## 4. Flutter auricular (FLUT)

`162 FLUT` concentra todos los casos en physician; `273 AFL` existe en diccionario pero con **0 casos** en physician de ambos hospitales (solo aparece residual en v24/software). `288 AFL-BL` = flutter con bloqueo 2:1.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 162 | FLUT | atrial flutter | 123,152 | 162,572 |
| 273 | AFL | atrial flutter | 0 | 0 |
| 288 | AFL-BL | atrial flutter with 2 to 1 block | 0 | 6,238 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 162 | FLUT | atrial flutter | 12,905 | 20,582 |
| 273 | AFL | atrial flutter | 0 | 0 |
| 288 | AFL-BL | atrial flutter with 2 to 1 block | 0 | 767 |

## 5. Taquicardia auricular y auricular multifocal

Taquicardias de origen auricular sostenido.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 164 | ATAC | atrial tachycardia | 0 | 26,256 |
| 280 | MULT-AT | multifocal atrial tachycardia | 0 | 14,292 |
| 279 | PO-ATP | possible wandering atrial pacemaker | 0 | 8,686 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 164 | ATAC | atrial tachycardia | 0 | 1,943 |
| 280 | MULT-AT | multifocal atrial tachycardia | 0 | 313 |
| 279 | PO-ATP | possible wandering atrial pacemaker | 0 | 408 |

## 6. Ritmos auriculares ectópicos / bajos

Marcapasos auricular fuera del nodo sinusal.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 30 | LAR | left atrial rhythm | 401 | 2,951 |
| 29 | RAR | low right atrial rhythm | 432 | 2,875 |
| 25 | RABRAD | low right atrial bradycardia | 95 | 2,404 |
| 26 | RATACH | low right atrial tachycardia | 11 | 7,879 |
| 27 | LABRAD | left atrial bradycardia | 36 | 8,587 |
| 28 | LATACH | left atrial tachycardia | 33 | 16,042 |
| 61 | EABRAD | unusual p axis, possible ectopic atrial bradycardia | 10,730 | 23,037 |
| 62 | EAR | unusual p axis, possible ectopic atrial rhythm | 45,116 | 14,219 |
| 63 | EATACH | unusual p axis, possible ectopic atrial tachycardia | 7,644 | 28,937 |
| 64 | EARO | ectopic atrial rhythm | 0 | 71,066 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 30 | LAR | left atrial rhythm | 0 | 64 |
| 29 | RAR | low right atrial rhythm | 0 | 59 |
| 25 | RABRAD | low right atrial bradycardia | 0 | 8 |
| 26 | RATACH | low right atrial tachycardia | 0 | 59 |
| 27 | LABRAD | left atrial bradycardia | 0 | 50 |
| 28 | LATACH | left atrial tachycardia | 0 | 644 |
| 61 | EABRAD | unusual p axis, possible ectopic atrial bradycardia | 1,071 | 704 |
| 62 | EAR | unusual p axis, possible ectopic atrial rhythm | 3,572 | 2,359 |
| 63 | EATACH | unusual p axis, possible ectopic atrial tachycardia | 537 | 625 |
| 64 | EARO | ectopic atrial rhythm | 0 | 3,741 |

## 7. Ritmo/taquicardia juncional

Origen entre aurícula y ventrículo.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 267 | JUNCT-R | junctional rhythm | 387,313 | 94,972 |
| 34 | JUNBRAD | junctional bradycardia | 8,603 | 5,520 |
| 270 | J-TACH | junctional tachycardia | 0 | 12,058 |
| 41 | JBRAD | unusual p axis and short pr, probable junctional bradycardia | 299 | 18,142 |
| 42 | JR | unusual p axis and short pr, probable junctional rhythm | 4,496 | 16,415 |
| 43 | JTACH | unusual p axis and short pr, probable junctional tachycardia | 5,285 | 23,688 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 267 | JUNCT-R | junctional rhythm | 7,789 | 7,492 |
| 34 | JUNBRAD | junctional bradycardia | 376 | 316 |
| 270 | J-TACH | junctional tachycardia | 0 | 87 |
| 41 | JBRAD | unusual p axis and short pr, probable junctional bradycardia | 21 | 87 |
| 42 | JR | unusual p axis and short pr, probable junctional rhythm | 352 | 331 |
| 43 | JTACH | unusual p axis and short pr, probable junctional tachycardia | 457 | 264 |

## 8. Taquicardia supraventricular (SVT) y QRS angosto

Latido rápido que baja por la vía normal (QRS angosto).

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 271 | SVT | supraventricular tachycardia | 29,873 | 10,518 |
| 266 | SUP-TACH | supraventricular tachycardia | 0 | 29,523 |
| 236 | NQTACH | narrow qrs tachycardia | 323 | 7,724 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 271 | SVT | supraventricular tachycardia | 2,130 | 207 |
| 266 | SUP-TACH | supraventricular tachycardia | 0 | 2,246 |
| 236 | NQTACH | narrow qrs tachycardia | 0 | 59 |

## 9. Latidos prematuros supraventriculares/auriculares (PAC)

Latidos adelantados de origen superior. `OCC/FREQ` = ocasionales/frecuentes. `BIGEM` = patrón cada-2-latidos. `CSEC` = consecutivos.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 222 | PAC | premature atrial complexes | 324,974 | 395,934 |
| 221 | PSVC | premature supraventricular complexes | 141,225 | 165,387 |
| 223 | PJC | premature junctional complexes | 0 | 316 |
| 211 | OCC | with occasional | 432,974 | 30,308 |
| 212 | FREQ | with frequent | 164,043 | 81,405 |
| 233 | CSEC | and consecutive | 75,331 | 16,712 |
| 234 | BIGEM | in a pattern of bigeminy | 32,872 | 16,048 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 222 | PAC | premature atrial complexes | 35,678 | 45,500 |
| 221 | PSVC | premature supraventricular complexes | 12,108 | 15,383 |
| 223 | PJC | premature junctional complexes | 0 | 17 |
| 211 | OCC | with occasional | 38,509 | 33,939 |
| 212 | FREQ | with frequent | 15,798 | 13,933 |
| 233 | CSEC | and consecutive | 3,121 | 2,297 |
| 234 | BIGEM | in a pattern of bigeminy | 3,923 | 2,566 |

## 10. Latidos prematuros ventriculares (PVC)

Latidos adelantados de origen ventricular, la extrasistolia más frecuente.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 231 | PVC | premature ventricular complexes | 1,130,305 | 575,399 |
| 232 | PVCF | premature ventricular and fusion complexes | 0 | 9,432 |
| 241 | PEC | premature ectopic complexes | 0 | 19,503 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 231 | PVC | premature ventricular complexes | 52,277 | 65,195 |
| 232 | PVCF | premature ventricular and fusion complexes | 0 | 130 |
| 241 | PEC | premature ectopic complexes | 0 | 22 |

## 11. Taquicardia / fibrilación ventricular (TV/FV) y ritmos ventriculares

Emergencias por ritmo ventricular rápido/desorganizado. `WQTACH/$SWQR` = taquicardia/QRS ancho. `$SVTACH/$SVFIB` = códigos internos de TV/FV (casi solo physician).

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 272 | VTACH | ventricular tachycardia | 0 | 8,265 |
| 277 | TVT | with transient ventricular tachycardia | 0 | 15,777 |
| 235 | WQTACH | wide qrs tachycardia | 11,823 | 20,413 |
| 237 | $SWQR | wide qrs rhythm | 129,089 | 29,470 |
| 248 | $SVTACH | ventricular tachycardia | 0 | 20,409 |
| 249 | $SVFIB | ventricular fibrillation | 0 | 161 |
| 268 | IDIO-R | idioventricular rhythm with av block | 0 | 375 |
| 269 | VENT-RTH | ventricular rhythm | 0 | 2,639 |
| 238 | $SIVR | idioventricular rhythm | 2,439 | 4,331 |
| 274 | VENT-FUS | with ventricular fusion | 0 | 348 |
| 244 | $SFUS | fusion complexes | 1,288,987 | 85,689 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 272 | VTACH | ventricular tachycardia | 0 | 34 |
| 277 | TVT | with transient ventricular tachycardia | 0 | 37 |
| 235 | WQTACH | wide qrs tachycardia | 1,091 | 1,292 |
| 237 | $SWQR | wide qrs rhythm | 9,046 | 3,642 |
| 248 | $SVTACH | ventricular tachycardia | 0 | 364 |
| 249 | $SVFIB | ventricular fibrillation | 0 | 12 |
| 268 | IDIO-R | idioventricular rhythm with av block | 0 | 19 |
| 269 | VENT-RTH | ventricular rhythm | 0 | 145 |
| 238 | $SIVR | idioventricular rhythm | 173 | 304 |
| 274 | VENT-FUS | with ventricular fusion | 0 | 23 |
| 244 | $SFUS | fusion complexes | 6,457 | 10,699 |

## 12. Bloqueos AV, SA y conducción

Retardos/interrupciones de la señal entre aurícula y ventrículo. No son “arritmia de ritmo” pura pero definen bradiarritmias.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 101 | FAV | with 1st degree av block | 575,095 | 397,193 |
| 102 | SPR | with short pr | 164,319 | 99,492 |
| 103 | MBZI | with 2nd degree av block (mobitz i) | 12,274 | 11,929 |
| 104 | MBZII | with 2nd degree av block (mobitz ii) | 6,515 | 5,580 |
| 105 | SAV | with 2nd degree av block | 8,600 | 61,411 |
| 106 | CHB | with complete heart block | 8,134 | 4,358 |
| 281 | COMP-HB | complete heart block | 0 | 4,388 |
| 107 | VAVB | with variable av block | 81,599 | 42,438 |
| 108 | AVDIS | with av dissociation | 10,936 | 10,944 |
| 141 | W2T1 | with 2:1 av conduction | 23,421 | 14,453 |
| 142 | W3T1 | with 3:1 av conduction | 4,923 | 5,395 |
| 143 | W4T1 | with 4:1 av conduction | 8,963 | 9,147 |
| 144 | W5T1 | with 5:1 av conduction | 769 | 4,644 |
| 190 | PROAV | with prolonged av conduction | 30,884 | 20,110 |
| 278 | WEKH | with mobitz i (wenckebach) block | 0 | 4,456 |
| 282 | AV-COND | suspect av conduction defect | 0 | 1,471 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 101 | FAV | with 1st degree av block | 68,601 | 72,804 |
| 102 | SPR | with short pr | 10,067 | 9,642 |
| 103 | MBZI | with 2nd degree av block (mobitz i) | 1,428 | 1,630 |
| 104 | MBZII | with 2nd degree av block (mobitz ii) | 307 | 228 |
| 105 | SAV | with 2nd degree av block | 451 | 4,148 |
| 106 | CHB | with complete heart block | 808 | 680 |
| 281 | COMP-HB | complete heart block | 0 | 176 |
| 107 | VAVB | with variable av block | 9,327 | 8,122 |
| 108 | AVDIS | with av dissociation | 784 | 948 |
| 141 | W2T1 | with 2:1 av conduction | 2,183 | 2,504 |
| 142 | W3T1 | with 3:1 av conduction | 302 | 635 |
| 143 | W4T1 | with 4:1 av conduction | 911 | 1,188 |
| 144 | W5T1 | with 5:1 av conduction | 61 | 437 |
| 190 | PROAV | with prolonged av conduction | 4,055 | 4,469 |
| 278 | WEKH | with mobitz i (wenckebach) block | 0 | 59 |
| 282 | AV-COND | suspect av conduction defect | 0 | 27 |

## 13. Pausas, escapes y bloqueos SA

Latidos de rescate o pausas del marcapasos natural.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 113 | PAUSE | with sinus pause | 0 | 1,940 |
| 242 | JESC | with junctional escape complexes | 11,354 | 3,957 |
| 243 | VESC | with ventricular escape complexes | 43,181 | 4,900 |
| 275 | J-ESC | with junctional escape | 0 | 7,364 |
| 276 | ESCBT | with escape beat | 0 | 2,842 |
| 111 | SABII | with 2nd degree sa block (mobitz ii) | 0 | 4,823 |
| 112 | SABI | with 2nd degree sa block (mobitz i) | 0 | 5,809 |
| 284 | SA-BLK | with sa block or transient av block | 0 | 400 |
| 285 | SAB | with sinus arrest or transient av block | 0 | 714 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 113 | PAUSE | with sinus pause | 0 | 192 |
| 242 | JESC | with junctional escape complexes | 184 | 408 |
| 243 | VESC | with ventricular escape complexes | 1,389 | 406 |
| 275 | J-ESC | with junctional escape | 0 | 839 |
| 276 | ESCBT | with escape beat | 0 | 149 |
| 111 | SABII | with 2nd degree sa block (mobitz ii) | 0 | 25 |
| 112 | SABI | with 2nd degree sa block (mobitz i) | 0 | 50 |
| 284 | SA-BLK | with sa block or transient av block | 0 | 25 |
| 285 | SAB | with sinus arrest or transient av block | 0 | 36 |

## 14. Ritmos con marcapasos y misceláneos de ritmo

Señal con dispositivo electrónico o morfologías asociadas.

### I0001 — MGH

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 295 | APR | atrial-paced rhythm | 41,871 | 34,674 |
| 296 | VPR | ventricular-paced rhythm | 62,086 | 74,257 |
| 297 | ASVPR | atrial-sensed ventricular-paced rhythm | 39,129 | 29,973 |
| 298 | AVDPR | av dual-paced rhythm | 20,703 | 18,172 |
| 289 | BIVPCK | biventricular pacemaker detected | 220 | 8,449 |
| 290 | PCK | electronic ventricular pacemaker | 0 | 85,250 |
| 292 | APCK | electronic atrial pacemaker | 0 | 49,697 |
| 293 | AVPCK | av sequential or dual chamber electronic pacemaker | 0 | 33,212 |
| 174 | CJP | with a competing junctional pacemaker | 39,219 | 14,654 |
| 175 | IRREG | with undetermined rhythm irregularity | 3,488 | 2,155 |
| 176 | IRR | irregular | 272 | 7,347 |
| 299 | UR | undetermined rhythm | 732,518 | 188,456 |

### I0006 — Emory

| Código | Acrónimo | Descripción | v24 | Physician |
|---|---|---|---:|---:|
| 295 | APR | atrial-paced rhythm | 5,501 | 6,267 |
| 296 | VPR | ventricular-paced rhythm | 8,829 | 7,521 |
| 297 | ASVPR | atrial-sensed ventricular-paced rhythm | 6,585 | 4,995 |
| 298 | AVDPR | av dual-paced rhythm | 3,349 | 4,363 |
| 289 | BIVPCK | biventricular pacemaker detected | 12 | 2,900 |
| 290 | PCK | electronic ventricular pacemaker | 0 | 16,149 |
| 292 | APCK | electronic atrial pacemaker | 0 | 9,689 |
| 293 | AVPCK | av sequential or dual chamber electronic pacemaker | 0 | 5,062 |
| 174 | CJP | with a competing junctional pacemaker | 2,844 | 1,539 |
| 175 | IRREG | with undetermined rhythm irregularity | 384 | 215 |
| 176 | IRR | irregular | 0 | 199 |
| 299 | UR | undetermined rhythm | 8,850 | 1,685 |

## Notas para la tesis (lectura de ingeniería)

- **Clases con volumen para entrenar en ambos hospitales:** NSR, SBRAD, STACH, AFIB, FLUT(162), PAC, PVC, JUNCT-R, FAV(101). Son las únicas con >10k casos por hospital en ambas fuentes.
- **Solo-MGH:** TV/FV y juncionales finas (272, 277, 248, 270, 266) casi no existen en Emory physician (decenas). Si la tesis las incluye, el test Emory no es viable para esas clases.
- **AFL=273 y 173/173:** `273 AFL` y `173 ABER2` tienen 0 en physician en ambos hospitales. No proponerlos como clase.
- **v24 vs physician:** v24 concentra ritmo común; physician añade lo raro (ATAC, MULT-AT, TVT, marcapasos). Para tesis multiclase usar physician; para benchmark reproducible usar v24.
- **Advertencia de etiquetado:** physician mezcla diagnósticos con gramática (`1301 COMPAR`, `1415 HAS-REP`, `1405/1418 no-longer`, `177 with`). Ver informe anterior de validación para la regla de limpieza antes de entrenar.
