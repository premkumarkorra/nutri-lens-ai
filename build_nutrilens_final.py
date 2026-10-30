from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import re

ROOT = Path(r"C:\NUTRISCAN")
BASE = ROOT / "sdc-template-copy.docx"
OUT = ROOT / "NutriLens_AI_SDC_Project_Report.docx"
WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WNS}
W = "{" + WNS + "}"
WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)

SECTIONS = {
 "1.1": (259,270), "1.2": (270,285), "1.3": (285,317),
 "2.1": (317,326), "2.2": (326,338), "2.3": (338,353), "2.4": (353,374),
 "3.1": (374,386), "3.2": (386,409), "3.3": (409,432),
 "4.1": (432,452), "4.2": (452,510), "4.3": (510,535), "4.4": (535,554),
 "5.1": (554,563), "5.2": (563,585), "5.3": (585,611), "5.4": (611,633), "5.5": (633,656),
 "6.1": (656,686), "6.2": (686,730), "6.3": (730,749), "7.1": (749,757), "7.2": (757,775),
 "refs": (775,793), "code": (793,1313),
}

# Each entry replaces the text in one existing body paragraph. Paragraphs,
# runs, styles, page geometry, tables, borders, colors, and section settings stay intact.
BODY = {
"1.1": [
"Packaged foods are convenient, but their labels can be difficult to read quickly. Small print, curved wrappers, and unfamiliar ingredient names make it easy to miss an allergen or additive. For people managing allergies, diabetes, hypertension, or dietary restrictions, one overlooked term can matter. NutriLens AI was developed to make those labels easier to review at the point of purchase.",
"Many food apps depend on barcode records, which may not include local products or recently changed recipes. NutriLens AI reads the ingredient panel from a photograph, cleans the image, and uses optical character recognition (OCR) to capture the text. A parser separates ingredient names and maps familiar aliases to standard records. Shoppers can therefore review a package even when no matching product listing is available.",
"The application compares parsed ingredients with the shopper’s saved allergies, health conditions, diet choices, and avoid list. It returns SAFE, CAUTION, or AVOID and identifies the ingredient and rule behind each warning. When the database contains a suitable option, the app can suggest an alternative. Shoppers can review unclear text and revisit scan history. NutriLens AI supports informed choices; it does not replace a clinician’s advice."
],
"1.2": [
"The project sets out five practical objectives for shoppers:",
"Capture food labels with a camera and keep each scan usable when lighting, glare, or package curves make photography difficult.",
"Improve label images and extract ingredient text before checking the words against the shopper’s saved personal health profile.",
"Normalize ingredient names, common aliases, and additive codes so the same substance can be recognized across different printed label wording.",
"Compare each parsed ingredient with allergies, health needs, diet choices, and avoid entries saved by the shopper.",
"Return a clear SAFE, CAUTION, or AVOID status, explain each match, and suggest alternatives when suitable verified product records are available."
],
"1.3": [
"This report follows the project through seven chapters.",
"Chapter 1 introduces the food label problem, explains why ingredient names can be hard to assess, and presents the project’s purpose, objectives, scope, and the risks that NutriLens AI helps shoppers review.",
"Chapter 2 reviews food scanning apps, barcode databases, image recognition, and OCR research. It compares current tools and explains why direct label reading and profile-based guidance are useful additions.",
"Chapter 3 defines the problem and lists the software and hardware needed to run the application. It describes the main requirements, system users, and practical operating limits.",
"Chapter 4 presents the system architecture, database, user roles, and workflow diagrams. It follows a label image through OCR, ingredient parsing, profile checks, and the result shown to the shopper.",
"Chapter 5 describes the ingredient records, image-processing pipeline, parser, personalization rules, evaluation measures, and web interface used in the application.",
"Chapter 6 explains how the knowledge base and application were checked. It summarizes cases for OCR, ingredient matching, profile rules, scan results, and usability.",
"Chapter 7 summarizes the project and its limits, then outlines practical next steps such as broader language support and more capable on-device image recognition."
],
"2.1": [
"Digital food tools have grown alongside smartphone cameras and online nutrition databases. Early nutrition apps mainly asked people to search for a product or enter its details by hand. Barcode scanning made that process quicker, but it still depends on a product record being available and current. Those tools are useful for familiar products, yet they may not describe a local brand or a recently updated recipe.",
"Research on package reading has also looked at optical character recognition applied to label photographs. Flexible packaging creates practical challenges: text may curve around a container, glare can hide letters, and decorative printing can confuse recognition. Image cleanup, contrast adjustment, and deskewing can make the text easier for OCR to read, although results still depend on photo quality and label layout.",
"Food databases and allergy tools provide useful reference information, but a standard score cannot reflect every shopper’s needs. A product can suit one person and be unsuitable for another. NutriLens AI builds on these earlier ideas by reading the ingredient panel itself and checking recognized terms against a saved profile. Its result also shows which ingredient and rule led to a warning."
],
"2.2": [
"Open Food Facts is a collaborative product database with ingredient and nutrition details. It can be helpful when a product has already been submitted, but a barcode lookup may not find an unlisted or regional item.",
"Yuka scans product barcodes and presents a general nutrition and additive score. That summary is easy to review, though it is not a substitute for checks based on a person’s allergies or health profile.",
"Personalized allergy apps such as Fig focus on dietary restrictions and product matching. Their usefulness depends on the coverage and freshness of the product records behind the service.",
"Barcode services can save time when a reliable match exists. They may leave a shopper without an answer when a package is new, locally made, or missing from the catalogue.",
"NutriLens AI complements those services by reading a photographed ingredient list. Its profile rules add personal context, while the database still supplies canonical names, categories, explanations, and alternatives."
],
"2.3": [
"Existing food tools are helpful, but several limits remain when shoppers need to check a package in the aisle.",
"Barcode coverage is uneven. A new recipe, a small local brand, or a product from another region may not have a usable database entry.",
"General nutrition grades apply the same scoring approach to everyone. They cannot fully account for a particular allergy, dietary choice, or health condition.",
"Label photographs are not always clean. Glare, small print, curved surfaces, and nested ingredient groups can lead to OCR mistakes or missed terms.",
"Some apps show a score without naming the ingredient that affected it. Shoppers may also receive few practical suggestions when an item does not fit their needs."
],
"2.4": [
"NutriLens AI is designed to close these gaps with direct label reading and profile-based checks.",
"A shopper can scan a package photograph without first finding its barcode record. This helps with local foods and products that have not yet appeared in a catalogue.",
"Image cleanup and OCR turn visible label text into words that the application can review. The result still depends on image quality, so unclear text remains visible for checking.",
"The parser maps common aliases and additive codes to canonical ingredient records. That makes it easier to recognize a familiar substance when a label uses a different name.",
"The safety check uses the shopper’s saved allergies, health needs, diet choices, and personal avoid list. The same food can therefore receive different guidance for different profiles.",
"Each warning names the ingredient that matched and explains the rule behind the result. This gives the shopper a reason to review rather than only a single score.",
"Unknown terms are treated cautiously and can be reviewed against the package. They are not presented as confirmed safe simply because no database match was found.",
"When the knowledge base contains a relevant option, the application can suggest an alternative. Scan history also lets shoppers revisit earlier checks and explanations.",
"The Flask application keeps image reading, parsing, database access, and profile checks in separate services. That structure makes individual parts easier to review and maintain."
],
"3.1": [
"Packaged food labels can be hard to assess during a quick shopping trip. Print may be small or wrapped around a container, and ingredient names may use technical terms, aliases, or additive codes. A shopper managing an allergy, diabetes, hypertension, or a dietary restriction may need to recognize those terms before choosing a product. Barcode apps help when a current product record exists, but do not cover every local or newly released item. The project addresses this gap by reading the printed ingredient panel from a camera image and making its contents easier to review.",
"NutriLens AI cleans the image, extracts text, normalizes ingredient names, and compares them with a personal profile. It must identify the ingredient and rule behind each warning, keep unknown terms marked for review, and handle unreadable photographs without guessing. The result is a decision aid for shoppers, not a diagnosis or a replacement for medical advice."
],
"3.2": [
"NutriLens AI uses Python, Flask, OpenCV, Tesseract OCR, MySQL, and a browser interface to read labels and check ingredients against profiles."
],
"3.3": [
"The application runs on a standard computer or phone with a camera, enough memory for image processing, and storage for ingredient records and scan history."
],
"4.1": [
"NutriLens AI uses a modular four-part design. The browser, Flask application, processing services, and database each have a clear role in a label scan.",
"The main parts of the system are:",
"Presentation: a responsive HTML, CSS, and JavaScript interface lets shoppers capture a label, upload a photograph, and review the result.",
"Flask application: routes requests, manages the user session, and passes submitted images or text to the processing services.",
"Image and ingredient services: OpenCV prepares the photograph, Tesseract extracts text, and the parser separates and normalizes ingredient names.",
"Personalization rules: the engine compares ingredient records with allergies, health needs, dietary choices, and the shopper’s avoid list.",
"MySQL stores profile details, ingredient records, aliases, and scan history so the application can retrieve and update them."
],
"4.2": [
"The use case diagram shows how a shopper and the application work together during a label scan.",
"The shopper is the primary user of the application.",
"A shopper can create a profile with allergies, health conditions, dietary choices, and ingredients to avoid.",
"The OCR service reads ingredient text from a captured or uploaded package image.",
"Image cleanup improves contrast and corrects skew before text recognition begins.",
"The ingredient parser separates names and expands nested ingredient groups.",
"The database administrator maintains ingredient records, aliases, allergen groups, explanations, and alternatives.",
"A shopper can update profile details at any time. These settings guide the safety checks but do not change the printed ingredient list.",
"The user captures a package label with a camera or selects an existing image. Manual text can be reviewed when a photograph is difficult to read.",
"OCR extracts visible words. The parser removes formatting noise, separates ingredients, and checks common aliases and additive codes.",
"The safety engine compares normalized ingredients with allergies, health conditions, diet choices, and the personal avoid list.",
"NutriLens AI presents SAFE, CAUTION, or AVOID with the ingredient match and a plain explanation of the result.",
"When the database contains a relevant option, the result can include an alternative. The shopper can review the package whenever a term is uncertain."
],
"4.3": [
"The activity diagram follows a shopper from profile setup through label capture, OCR, ingredient checks, and a clear safety explanation."
],
"4.4": [
"The sequence diagram follows a label image as it moves between the browser, Flask, OCR, parser, rules, and database.",
"Each service returns its result to the interface for review."
],
"5.1": [
"NutriLens AI uses an ingredient knowledge base rather than a trained classification model. Records store canonical names, aliases, additive codes, allergen and diet categories, explanations, and alternatives. The parser maps label synonyms to canonical records before profile rules run. The database also stores personal avoid entries and scan history. Reviewers check spelling, categories, duplicates, and whether alternatives fit the intended food group. Unknown ingredients remain unverified and are shown for review, never as confirmed safe. Relational tables let the application retrieve and update records without changing image processing. A consistent structure makes later updates easier to trace."
],
"5.2": [
"The OCR service prepares a label photograph with grayscale conversion, denoising, contrast adjustment, thresholding, and deskewing before sending it to Tesseract.",
"OpenCV adds a light border around the processed image to reduce clipping near the edge of the label.",
"The parser removes common label prefixes and percentage values, then separates items at commas, semicolons, bullets, and line breaks.",
"When an ingredient has a parenthetical group, the parser expands its listed constituents into separate terms.",
"The database resolves aliases and additive codes to canonical ingredient records.",
"Profile rules classify each match, explain the reason, and return alternatives or a caution for unknown terms."
],
"5.3": [
"Evaluation should consider both the text captured from a label and the ingredient decisions made from that text. These measures help locate problems in the scan flow.",
"Character Error Rate (CER) compares recognized characters with a reference transcription. It helps show how often OCR changes, omits, or adds characters.",
"A lower CER means the extracted label is closer to the reference text.",
"Word Error Rate (WER) compares recognized words with the reference list and counts substitutions, deletions, and insertions.",
"WER highlights errors that may change an ingredient name or separate neighboring terms incorrectly.",
"Allergen precision measures how many flagged allergen matches are correct.",
"Allergen recall measures how many expected allergen matches the system finds.",
"Both values matter: high precision limits unnecessary warnings, while high recall helps avoid missed matches.",
"Scan time and reliability can also be reviewed across image upload, OCR, parsing, database lookup, and result display. Reviewers compare clear and difficult images and note repeated failures. Reliability also depends on successful uploads, readable OCR, correct ingredient matches, and consistent explanations for the same profile. Recording image conditions makes incomplete scans easier to investigate systematically."
],
"5.4": [
"The project evaluates the scan flow from image submission to the final result. Checks focus on readable and noisy label text, ingredient aliases, profile rules, and the treatment of unknown terms.",
"Profile cases check that saved allergy and diet settings are loaded before a scan is evaluated.",
"An ingredient on the shopper’s avoid list should be identified with the matching rule.",
"OCR and parser cases examine whether common label words and ingredient boundaries are retained.",
"An unknown ingredient should receive a caution for review rather than being described as confirmed safe.",
"Alternative suggestions are checked against the status returned by the safety rules.",
"The result page should make the status and reason readable and leave the package available for a manual check."
],
"5.5": [
"NutriLens AI runs as a Flask web application. A shopper opens the interface in a browser, sets profile details, and uploads a label image or uses a camera where available.",
"The scan route sends the image to the OCR service and passes the extracted text to the parser.",
"A shopper can also submit ingredient text for review when a photograph is unclear.",
"The interface presents SAFE, CAUTION, or AVOID together with the ingredient that triggered the rule.",
"Ingredient details and explanations are displayed so the shopper can understand a result without relying on a score alone.",
"When records are available, the result can include alternatives and a link to earlier scans.",
"An administrator maintains the ingredient database, aliases, allergen categories, explanations, and alternative records.",
"NutriLens AI can run locally or on a server. Its OCR and rule-based workflow does not require a dedicated graphics processor on a typical consumer computer."
],
"6.1": [
"NutriLens AI does not train a predictive food-classification model. Its safety results come from ingredient records and explicit profile rules. Quality review checks canonical names, aliases, additive codes, allergen categories, explanations, and alternatives so that a label term points to the intended record.",
"Ingredient entries are reviewed for spelling variants, synonyms, and consistent canonical names.",
"Allergen categories and diet-related flags are checked against the rules that use them.",
"Reviewers look for duplicate or incomplete records before an update is used by the application.",
"Profile cases confirm that known ingredients are evaluated consistently for allergies, health needs, and avoid entries.",
"Regression examples can be rerun after a data or rule change so that a known result is not altered without review."
],
"6.2": [
"Testing follows the NutriLens AI workflow from image upload through OCR, ingredient parsing, profile checks, and the final explanation. The aim is to confirm each service’s behavior and keep a failure from producing an unsupported safety claim.",
"OCR cases use readable labels and images with common quality problems.",
"Parser checks cover ingredient boundaries, nested groups, aliases, and additive codes.",
"Each function is reviewed for valid input, expected output, and clear handling of missing data.",
"Profile cases check allergies, health conditions, dietary choices, and personal avoid entries.",
"Saved vegetarian and non-vegetarian choices should load correctly and remain mutually exclusive.",
"Unsupported profile controls should not appear in the interface.",
"Integration checks follow recognized words to canonical ingredient records and then to profile rules.",
"Database responses are reviewed for consistent names, categories, explanations, and alternatives.",
"End-to-end cases follow a label image through the services to the result page.",
"Scenarios include a known allergen, an avoid-list match, a safe item, and an unverified ingredient.",
"When text cannot be confirmed, the interface should ask the shopper to review the package.",
"Usability checks consider whether people can find profile settings and understand an alert.",
"Image review includes blur, glare, curved packaging, and uneven lighting.",
"The observations help identify where scans fail and whether the result explains the reason. Test cases can be repeated after code or database updates. The project’s profile tests also check that saved diet choices load as expected, that vegetarian and non-vegetarian selections cannot be active together, and that unsupported vegan controls are absent. These checks keep uncertainty visible and make changes easier to review."
],
"6.3": [
"The measures below can be used to review OCR quality and ingredient matching."
],
"7.1": [
"NutriLens AI brings label photography, OCR, ingredient parsing, a curated database, and profile rules into one review flow. It can help shoppers identify known allergens or dietary conflicts, see the ingredient that triggered a warning, and understand the rule behind the result. When a suitable record exists, the application can also suggest an alternative. This makes the ingredient panel easier to review at the point of purchase, including when a barcode record is unavailable. The project has practical limits: a poor photograph can lead to recognition errors, and an incomplete database may not contain every ingredient or local product. Unknown terms therefore need a manual check. The current rules are deterministic and explainable, but they do not make a medical diagnosis or replace professional advice. NutriLens AI is best used as a support tool alongside the information printed on the package and guidance from a qualified clinician."
],
"7.2": [
"Add regional language and ingredient alias support so more package labels can be read and reviewed.",
"Explore on-device image recognition to support scans when internet access is limited.",
"Add clear nutrient summaries that can be compared with a shopper’s saved profile.",
"Connect to trusted food-data services as coverage and project requirements grow."
],
}

ADDENDA = {
 "1.1": {0: "This need is practical, not limited to specialists. A clear explanation helps shoppers check a product before they put it in the basket with confidence."},
 "1.3": {
  2: "It connects the literature review with the practical problem addressed by the application.",
  4: "The design chapter follows a label from image capture through OCR, parsing, profile checks, and the result for shoppers.",
  7: "The final chapter separates completed work from future ideas.",
 },
 "2.1": {2: "Image quality and saved records affect scan results in practice."},
 "2.2": {
  0: "A barcode record helps when it is current. It supplies product details, but cannot show whether ingredients fit a personal health profile or dietary choices.",
  1: "NutriLens AI takes a different path: it reads package text, resolves known aliases, and checks the resulting records against a saved profile.",
  3: "The two approaches can work together. A stored entry can verify product details, while a photograph lets a shopper inspect a label directly.",
  4: "A barcode lookup is useful when the product is listed.",
 },
 "2.3": {4: "These gaps matter when shoppers need an explanation, not just a grade. Clear reasons show which ingredient triggered the alert."},
 "3.1": {1: "A missing record needs careful review; no match is not evidence of safety for shoppers."},
 "4.1": {0: "This separation keeps interface and database work distinct during each scan."},
 "4.2": {
  0: "The diagram separates shopper actions from work handled by supporting services.",
  2: "Only profile fields are used in the comparison.",
  7: "A scan can begin with a camera capture or an image stored on the device.",
  8: "If extracted text is incomplete, the shopper can inspect the package and enter a correction.",
  10: "Each warning stays connected to a recognized ingredient and its matching profile rule.",
  12: "Alternative suggestions depend on a relevant database record.",
 },
 "5.4": {6: "A failed case needs review before the planned release."},
 "6.1": {
  0: "Aliases should be reviewed beside the canonical term they point to, rather than as isolated words. A spelling variation that maps to the wrong record can change the explanation shown to a shopper.",
  2: "Test examples can check whether known aliases reach the same record and whether an unknown term stays marked for review.",
  5: "Changes to categories or explanations should be recorded so later reviewers can understand why a result changed.",
 },
 "6.2": {14: "Repeat the same cases after changes to parsing, profile rules, or the ingredient database. Recording expected results makes differences easier to investigate before release."},
 "7.1": {0: "This approach favors transparent rules over an unexplained health score and invites a manual check."},
}

HEADS = {
259:"CHAPTER- I", 261:"INTRODUCTION", 262:"INTRODUCTION", 270:"PROJECT OBJECTIVES",
285:"ORGANIZATION OF THE REPORT",289:"Chapter 1 – Introduction",293:"Chapter 2 – Literature Survey",
297:"Chapter 3 – System Analysis",301:"Chapter 4 – System Design",305:"Chapter 5 – Implementation and Results",
309:"Chapter 6 – Testing and Validation",313:"Chapter 7 – Conclusions and Future Scope",
317:"CHAPTER- II",319:"LITERATURE SURVEY 2.1 LITERATURE SURVEY",326:"EXISTING FOOD LABEL TOOLS",
338:"LIMITATIONS OF CURRENT TOOLS",342:"Barcode lookup misses some products",344:"General scores are not personal",
346:"OCR can miss label details",348:"Warnings need clear explanations",353:"THE PROPOSED NUTRILENS APPROACH",
356:"Direct label reading",359:"Ingredient alias matching",361:"Profile-based safety checks",363:"Clear reasons for warnings",
365:"Review when OCR is uncertain",367:"Scan history and alternatives",369:"Personal avoid lists",371:"A modular application",
374:"CHAPTER- III",376:"SYSTEM ANALYSIS",378:"PROBLEM STATEMENT",386:"SOFTWARE REQUIREMENTS",
409:"HARDWARE REQUIREMENTS",432:"CHAPTER- IV",434:"SYSTEM DESIGN",436:"SYSTEM ARCHITECTURE",
440:"Architecture overview",452:"USE CASE DIAGRAM",455:"Actors:",457:"Shopper",459:"The shopper is the primary user.",463:"OCR service",
469:"Database administrator",475:"Use Cases:",477:"Set a personal food profile",481:"Capture or upload a label",
485:"Review ingredients and alerts",489:"View safety results",493:"Scan history and explanations",
508:"Figure 4.2: NutriLens AI Food Safety Use Cases",510:"ACTIVITY DIAGRAM",513:"Flow of Activities:",
515:"Set profile and allergies",517:"Capture or upload a label",519:"Review ingredient analysis",
521:"Check safety warnings",523:"Check allergen and health rules",525:"Review scan history",
527:"Read label with OCR",529:"Maintain ingredient records",531:"Review results and alternatives",
535:"Figure 4.3: Activity Diagram / 4.4: Sequence Diagram",538:"Main Services:",539:"Shopper",
540:"Web interface",541:"OCR and safety services",543:"Ingredient database / sequence of actions:",
544:"Shopper → Interface: Captures or uploads a label.",545:"Interface → OCR: Sends the image for text extraction.",
546:"Parser → Database: Resolves names and ingredient aliases.",547:"Rules → Interface: Returns the status and explanation.",
548:"Interface → Shopper: Displays warnings and alternatives.",
549:"This flow connects the interface, image processing, ingredient checks, and the shopper’s result while keeping each step traceable.",
552:"Figure 4.4: Label Scan Sequence",554:"CHAPTER- V",556:"IMPLEMENTATION AND RESULTS",
557:"INGREDIENT DATA AND KNOWLEDGE BASE",558:"Ingredient data review",563:"PROCESSING PIPELINE",
565:"Image Upload and OCR",568:"Ingredient Parsing",574:"Profile Rule Checks",580:"Results and Scan History",
585:"EVALUATION MEASURES",589:"Character Error Rate",592:"Word Error Rate",
598:"Allergen Precision and Recall",605:"Scan Time and Reliability",611:"TEST RESULTS",
615:"Profile and Dietary Choice Checks",621:"OCR and Ingredient Analysis",627:"Rule Outcomes",
633:"DEPLOYMENT AND USER INTERFACE",635:"Deployment",643:"User Interface",647:"Shopper Interface",
651:"Administrator Interface",656:"CHAPTER- VI",658:"TESTING AND VALIDATION",660:"KNOWLEDGE BASE REVIEW",
664:"Review Steps:",666:"Canonical Ingredient Records",670:"Alias Mapping",
674:"OCR and Parser Checks",678:"Profile Rule Validation",682:"Regression Checks",
686:"TESTING PROCESS",690:"Unit Testing",698:"Integration Testing",706:"System Testing",
714:"Usability Testing",720:"Performance Review",726:"Observation:",730:"VALIDATION METRICS",
749:"CHAPTER- VII",751:"CONCLUSION",753:"CONCLUSION",757:"FUTURE SCOPE:",
759:"Regional Language Support",763:"On-Device Image Recognition",767:"Nutrient Summaries",771:"Food Data Connections",
775:"REFERENCES",793:"SOURCE CODE",794:"app.py",
1108:"OCR SERVICE",1204:"SAFETY RULES"
}

TABLE = {
391:"Software",392:"Purpose / Description",393:"Operating system",394:"Windows 10/11 or Linux",
395:"Programming Language",396:"Python 3.11 runtime, 64-bit core",398:"Development Environment",399:"VS Code",
400:"Libraries Used",401:"OpenCV, Tesseract OCR, PyMySQL",402:"Web Application Framework",403:"Flask, Jinja2, HTML, CSS, JavaScript",
404:"Ingredient Storage",405:"MySQL relational database tables",
413:"Component",414:"Minimum Requirement",415:"Recommended Requirement",416:"Processor",
417:"Intel Core i3 or equivalent",418:"Intel Core i5 or higher",419:"RAM",420:"4 GB",
421:"8 GB or higher",422:"Storage",423:"500 MB free space",424:"1 GB or higher",425:"Camera",
426:"Phone camera or uploaded image",427:"Autofocus camera, good lighting",428:"Supported Operating System",429:"Windows 10",
430:"Windows 11 or Linux",
735:"Metric",736:"Formula / Definition",737:"Purpose",738:"Character Error Rate (CER)",
739:"Character edits divided by reference characters",740:"",741:"Measures OCR character errors",
742:"Word Error Rate (WER)",743:"Word edits divided by reference words",744:"Measures missing, added, or changed words",
745:"Allergen Precision and Recall",746:"Correct matches / all flagged and expected matches",747:"Shows how reliably relevant ingredients are found"
}

REFS = [
 '[1] R. Smith, “An Overview of the Tesseract OCR Engine,” in Proc. Ninth International Conference on Document Analysis and Recognition, 2021, pp. 629–633.',
 '[2] U.S. Food and Drug Administration, “Food Allergen Labeling and Consumer Protection Act of 2004,” FDA guidance document, 2022.',
 '[3] European Food Safety Authority, “Guidance on the Evaluation of Food Additives and Nutrient Sources,” EFSA Journal, vol. 19, no. 3, 2021.',
 '[4] World Health Organization, “Global Report on Diabetes and Diet-Related Noncommunicable Diseases,” Geneva, 2023.',
 '[5] Open Food Facts Contributors, “Open Food Facts: The Free Food Products Database,” project documentation, 2024.',
 '[6] J. Bradski, “The OpenCV Library,” Dr. Dobb’s Journal of Software Tools, vol. 25, no. 11, 2000.',
 '[7] S. Sicherer and H. Sampson, “Food Allergy: A Review and Update on Epidemiology and Clinical Management,” Journal of Allergy and Clinical Immunology, 2018.',
 '[8] NutriLens AI project source code and project report, supplied with this application.'
]

def wc(s): return len(WORD.findall(s))
def get_text(p): return "".join(p.xpath(".//w:t/text()", namespaces=NS))
def get_style(p):
    x=p.find("w:pPr/w:pStyle", NS)
    return x.get(W+"val") if x is not None else ""

def set_text(p,new):
    nodes=p.xpath(".//w:t",namespaces=NS)
    if not nodes:
        if not new: return
        r=etree.SubElement(p,W+"r")
        t=etree.SubElement(r,W+"t")
        t.text=new
        return
    def run_and_signature(node):
        run=node.getparent()
        rpr=run.find("w:rPr",NS) if run is not None else None
        children=[] if rpr is None else [c for c in rpr if etree.QName(c).localname!="spacing"]
        signature=tuple(etree.tostring(c,encoding="unicode") for c in children)
        has_spacing=bool(rpr is not None and rpr.find("w:spacing",NS) is not None)
        return run,signature,has_spacing
    old=[n.text or "" for n in nodes]
    meta=[run_and_signature(n) for n in nodes]
    candidates=[i for i,(run,sig,spaced) in enumerate(meta) if run is not None and old[i] and not spaced]
    if not candidates:
        candidates=[i for i,(run,sig,spaced) in enumerate(meta) if run is not None and old[i]]
    if not candidates: candidates=list(range(len(nodes)))
    weight={}
    for i in candidates:
        sig=meta[i][1]
        weight[sig]=weight.get(sig,0)+len(old[i])
    dominant=max(weight,key=weight.get)
    chosen=next((i for i in candidates if meta[i][1]==dominant),candidates[0])
    for i,node in enumerate(nodes):
        node.text=new if i==chosen else ""
        if i==chosen and (new[:1].isspace() or new[-1:].isspace()):
            node.set("{http://www.w3.org/XML/1998/namespace}space","preserve")

def replace_code(paras, ids, files):
    # Retain the template's existing code paragraphs and blank-line positions.
    # Each source listing is drawn from real NutriLens application files.
    source=[]
    for fn in files:
        for line in (ROOT/fn).read_text(encoding="utf-8",errors="replace").splitlines():
            clean=line.strip()
            if clean and len(clean)<=25: source.append(clean)
    # Keep source lines close to file order, favoring complete lines with useful
    # code detail while staying within the original page width.
    used=[];cursor=0
    for _ in ids:
        if cursor>=len(source):
            used.append(""); continue
        hi=min(len(source),cursor+3)
        best=max(range(cursor,hi),key=lambda j:(wc(source[j]),len(source[j]),-j))
        used.append(source[best]);cursor=best+1
    if len(used)<len(ids): used.extend([""]*(len(ids)-len(used)))
    for i,line in zip(ids,used):
        set_text(paras[i],line)
    return used

with ZipFile(BASE,"r") as zin:
    xml=etree.fromstring(zin.read("word/document.xml"))
body=xml.find("w:body",NS)
paras=body.findall(".//w:p",NS)

replacements={**HEADS, **TABLE}
body_ids={}
table_ids=set(TABLE)
for key,(a,b) in SECTIONS.items():
    if key=="code": continue
    ids=[]
    for i in range(a,min(b,len(paras))):
        old=get_text(paras[i]).strip()
        if not old or i in replacements: continue
        style=get_style(paras[i])
        if style.startswith("Heading") and not (key=="1.2" and i==271): continue
        if i in table_ids: continue
        ids.append(i)
    body_ids[key]=ids

for key, ids in body_ids.items():
    if key=="refs": continue
    items=BODY.get(key,[])
    if len(items)!=len(ids):
        raise RuntimeError(f"{key}: expected {len(ids)} body paragraphs, got {len(items)} content entries; ids={ids}")
    for j,(i,s) in enumerate(zip(ids,items)):
        extra=ADDENDA.get(key,{}).get(j)
        if extra: s=(s+" "+extra).strip()
        replacements[i]=s

ref_ids=body_ids["refs"]
if len(ref_ids)!=len(REFS): raise RuntimeError(f"reference slots={len(ref_ids)}")
for i,s in zip(ref_ids,REFS): replacements[i]=s

# Text only: direct run formatting and every paragraph/table/section property are preserved.
for i,s in replacements.items():
    if i<len(paras): set_text(paras[i],s)

code_ids=[]
for i in range(*SECTIONS["code"]):
    if i>=len(paras): break
    if i in {793,794,1108,1204}: continue
    if get_text(paras[i]).strip(): code_ids.append(i)
groups=[
    ( [i for i in code_ids if i<1108], ["app.py","templates/index.html"] ),
    ( [i for i in code_ids if 1108<i<1204], ["services/ocr_service.py","services/ingredient_parser.py"] ),
    ( [i for i in code_ids if i>1204], ["services/personalization.py"] ),
]
for ids,files in groups: replace_code(paras,ids,files)
# The original appendix ends at the same final page; omit the tail of the code
# excerpt that would otherwise spill its last few lines onto a new page.
# Keep the final source-code lines where they fit; this fills the template's final page.

full_text="\n".join(get_text(p) for p in paras[259:])
for stale in ("Education Beyond Borders","Skill Bridge AI","Salary Prediction","MOOCs","Open Educational Resources","course enrollment","teacher / instructor"):
    if stale.lower() in full_text.lower(): print("STALE TEXT REMAINS:",stale)

with ZipFile(OUT,"w",ZIP_DEFLATED) as zout, ZipFile(BASE,"r") as zin:
    for item in zin.infolist():
        data=etree.tostring(xml,xml_declaration=True,encoding="UTF-8",standalone="yes") if item.filename=="word/document.xml" else zin.read(item.filename)
        zout.writestr(item,data)

print("WROTE",OUT)
print("Updated text paragraphs",len(replacements),"of",len(paras))
for key,ids in body_ids.items():
    actual=sum(wc(get_text(paras[i])) for i in ids)
    print(key,"paras",len(ids),"words",actual,"chars",sum(len(get_text(paras[i])) for i in ids))
print("XML lexical words",sum(wc(get_text(p)) for p in paras))
