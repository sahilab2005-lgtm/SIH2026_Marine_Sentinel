import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "C:/Users/Acer/Downloads/SIH2026-IDEA-Presentation-Format (1).pptx";
const deck = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await deck.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  include: "id,slide,name,title,textPreview,text,bbox,isPlaceholder,placeholders",
  maxChars: 30000,
});
console.log(snapshot.ndjson);
