import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const root = "C:/Users/Acer/OneDrive/MarineDebrisAI";
const skill = "C:/Users/Acer/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const template = "C:/Users/Acer/Downloads/SIH2026-IDEA-Presentation-Format (1).pptx";
const out = path.join(root, "deliverables", "MarineSentinel_SIH2026_IdeaPresentation.pptx");
const tmp = path.join(root, ".codex-finalizer", "marine_sentinel_candidate.pptx");
const team = "TEAM [NAME]";
const deck = await PresentationFile.importPptx(await FileBlob.load(template));
const set = (id, text, frame, style = { typeface: "Arial", fontSize: 20, color: "1F4E79" }) => { const x = deck.resolve(id); x.text = text; x.text.style = style; if (frame) x.frame = frame; };
const rep = (id, before, after) => deck.resolve(id).text.replace(before, after);

set("sh/7qp4be9c", "\nMARINE SENTINEL");
set("sh/wn6dc7eh", "\nProblem Statement ID: [Enter SIH ID]\nProblem Statement: AI-Powered Automated Underwater Marine Debris and Anomaly Detection System using Side-Scan Sonar Imagery\nTheme: [Enter SIH theme]\nPS Category: Software\nTeam ID: [Enter team ID]\n" + team);
deck.resolve("sh/7qp4be9c").text.style = { typeface: "Arial", fontSize: 32, bold: true, color: "1F4E79" };
deck.resolve("sh/wn6dc7eh").text.style = { typeface: "Arial", fontSize: 17, color: "1F4E79" };

set("sh/dkvmpszm", "MARINE SENTINEL");
set("sh/qx4nud0b", "Local dashboard for side-scan sonar review\n\nUpload sonar imagery and survey metadata\nCondition scans for speckle noise and uneven contrast\nDetect crab pots and debris with trained YOLO inference\nShow confidence, dimensions and approximate coordinates\nExport a field report for cleanup and AUV teams", { left: 54, top: 210, width: 630, height: 320 });
rep("sh/ove9o7yd", "Your Team Name", team);
deck.resolve("sh/dkvmpszm").text.style = { typeface: "Arial", fontSize: 32, bold: true, color: "1F4E79" };
deck.resolve("sh/qx4nud0b").text.style = { typeface: "Arial", fontSize: 18, color: "1F4E79" };
deck.resolve("sh/ove9o7yd").text.style = { typeface: "Arial", fontSize: 11, bold: true, color: "1F4E79" };
deck.slides.getItem(1).images.add({ blob: await fs.readFile("C:/Users/Acer/AppData/Local/Temp/codex-clipboard-ec154b60-d1ec-4393-8219-640f04105b22.png"), contentType: "image/png", alt: "Marine Sentinel prototype dashboard", fit: "contain", geometry: "roundRect", borderRadius: "rounded-xl", position: { left: 722, top: 220, width: 455, height: 310 } });

set("sh/j6dgf6tk", "TECHNICAL APPROACH");
set("sh/1k3214v2", "Input\nSide-scan sonar image with location and scale metadata\n\nImage conditioning\nNon-local means denoising and CLAHE local contrast normalization\n\nObject detection\nTrained YOLO11n model for Crab-Pot and Maybe-Crab-Pot labels\n\nDecision support\nConfidence threshold and IoU suppression reduce duplicate boxes\n\nOutput\nAnnotated scan plus JSON and CSV anomaly report", { left: 54, top: 185, width: 620, height: 410 });
rep("sh/m1c3mlsn", "Your Team Name", team);
deck.resolve("sh/j6dgf6tk").text.style = { typeface: "Arial", fontSize: 32, bold: true, color: "1F4E79" };
deck.resolve("sh/1k3214v2").text.style = { typeface: "Arial", fontSize: 17, color: "1F4E79" };
deck.resolve("sh/m1c3mlsn").text.style = { typeface: "Arial", fontSize: 11, bold: true, color: "1F4E79" };
deck.slides.getItem(2).images.add({ blob: await fs.readFile("C:/Users/Acer/OneDrive/MarineDebrisAI/dataset/yolo/images/test/baycove_07_06_png_jpg.rf.5a2e74f04f707fe66f050a3b61fcd7c2.jpg"), contentType: "image/jpeg", alt: "Side-scan sonar test image", fit: "cover", geometry: "roundRect", borderRadius: "rounded-xl", position: { left: 710, top: 205, width: 400, height: 300 } });

set("sh/ud8fyt4z", "FEASIBILITY AND VIABILITY");
set("sh/sjad83id", "Dataset readiness\nThe project includes YOLO-formatted training, validation and held-out test splits for two debris classes.\n\nBuild readiness\nThe prototype uses Python, Streamlit, OpenCV and Ultralytics YOLO. A trained best.pt model now resides in the project models folder.\n\nDeployment path\nTrain or resume on Google Colab GPU, evaluate on held-out test data and run local inference in the dashboard.\n\nRisk control\nOperators review low-confidence targets before field action.");
rep("sh/i94r6xgz", "Your Team Name", team);
deck.resolve("sh/ud8fyt4z").text.style = { typeface: "Arial", fontSize: 32, bold: true, color: "1F4E79" };
deck.resolve("sh/sjad83id").text.style = { typeface: "Arial", fontSize: 18, color: "1F4E79" };
deck.resolve("sh/i94r6xgz").text.style = { typeface: "Arial", fontSize: 11, bold: true, color: "1F4E79" };

set("sh/y1g7ylcj", "IMPACT AND BENEFITS");
set("sh/g7alsnu1", "Conservation teams can prioritise sonar regions for human review instead of examining full sonar logs manually.\n\nCleanup and vessel teams receive a structured report containing target class, confidence, dimensions, priority and estimated coordinates.\n\nLocal inference supports offshore missions with intermittent connectivity.\n\nHuman review remains part of the workflow for ambiguous targets and safety-critical decisions.");
rep("sh/ahkvi1cb", "Your Team Name", team);
deck.resolve("sh/y1g7ylcj").text.style = { typeface: "Arial", fontSize: 32, bold: true, color: "1F4E79" };
deck.resolve("sh/g7alsnu1").text.style = { typeface: "Arial", fontSize: 18, color: "1F4E79" };
deck.resolve("sh/ahkvi1cb").text.style = { typeface: "Arial", fontSize: 11, bold: true, color: "1F4E79" };

set("sh/1kj2p0ve", "RESEARCH AND REFERENCES");
set("sh/vq5cve1s", "NOAA Marine Debris Program\nhttps://marinedebris.noaa.gov/what-marine-debris/derelict-fishing-gear\n\nFAO Responsible Fishing Practices\nhttps://www.fao.org/responsible-fishing/en\n\nUltralytics YOLO custom-data documentation\nhttps://docs.ultralytics.com/yolov5/tutorials/train-custom-data\n\nProject evidence\nYOLO-format Crab-Pot and Maybe-Crab-Pot sonar dataset included in this project", { left: 64, top: 180, width: 900, height: 420 });
rep("sh/pc76hkr2", "Your Team Name", team);
deck.resolve("sh/1kj2p0ve").text.style = { typeface: "Arial", fontSize: 32, bold: true, color: "1F4E79" };
deck.resolve("sh/vq5cve1s").text.style = { typeface: "Arial", fontSize: 18, color: "1F4E79" };
deck.resolve("sh/pc76hkr2").text.style = { typeface: "Arial", fontSize: 11, bold: true, color: "1F4E79" };

deck.slides.remove(6);
for (let i = 0; i < 6; i++) deck.slides.getItem(i).speakerNotes.textFrame.setText(i === 5 ? "Sources: NOAA Marine Debris Program, FAO Responsible Fishing Practices, Ultralytics documentation." : "Marine Sentinel SIH prototype.");
await (await PresentationFile.exportPptx(deck)).save(tmp);
const { finalizePresentation } = await import(pathToFileURL(path.join(skill, "container_tools", "artifact_tool_utils.mjs")).href);
await finalizePresentation({ sourceTemplatePath: template, workspaceDir: root, candidatePath: tmp, finalPath: out, pythonExecutable: "C:/Users/Acer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe", integrityValidatorPath: path.join(skill, "container_tools", "inspect_presentation_package_integrity.py"), layoutValidatorPath: path.join(skill, "container_tools", "inspect_presentation_layout_geometry.py"), layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"], explicitTotalSlideCount: 6, fontPolicy: { basis: "reference", families: ["Arial"], referencePath: template, referenceSha256: "ce3e5deebec2741f3383cb2dd21269cad8d9930f7c747c9903d7d4b27db14de6" }, verifyArtifactToolImport: true, receiptPath: path.join(root, ".codex-finalizer", "deck-validation.json") });
console.log(out);
