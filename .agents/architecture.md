# Redactietool sequence overview

## Participants

- Redactietool
- MediaHaven
- Elastic Search
- Suggest SPARQL service
- FTP Server
- SAML server

## Authentication flow

1. Redactietool → SAML server: Login with SAML credentials
2. SAML server → Redactietool: Return session
3. Redactietool → Redactietool: Redirect to protected search page

---

## PID search loop

4. Redactietool → MediaHaven: Search for PID
5. MediaHaven → Redactietool: `getMetadataResponse`

---

## Metadata bewerken

6. Redactietool → Redactietool: Redirect to metadata edit page
7. Redactietool → MediaHaven: Get `publicatie_status`
8. Redactietool → MediaHaven: Get subtitle object
9. MediaHaven → Redactietool: Return metadata, `publicatie_status`, and subtitles
10. Redactietool → Redactietool: Update metadata, leerobject, language, type, ...

### Load leerobject metadata lists

11. Redactietool → Suggest SPARQL service: Request onderwijsniveaus
12. Suggest SPARQL service → Redactietool: Return onderwijsniveaus list
13. Redactietool → Suggest SPARQL service: Request onderwijsgraden
14. Suggest SPARQL service → Redactietool: Return onderwijsgraden list
15. Redactietool → Suggest SPARQL service: Request themas
16. Suggest SPARQL service → Redactietool: Return themas list
17. Redactietool → Suggest SPARQL service: Request vakken
18. Suggest SPARQL service → Redactietool: Return vakken list

### Select and suggest vakken loop

19. Redactietool → Redactietool: Select onderwijsniveaus and graden
20. Redactietool → Redactietool: Select themas
21. Redactietool → Suggest SPARQL service: Request suggested vakken with parameters `(graden, themas)`
22. Suggest SPARQL service → Redactietool: Return suggested vakken
23. Redactietool → Suggest SPARQL service: Request related vakken with parameters `(niveau, graden)`
24. Suggest SPARQL service → Redactietool: Return related vakken
25. Redactietool → Redactietool: Select vakken for this item from suggestions, related vakken in modal, or all vakken in dropdown

### Keyword search loop

26. Redactietool → Elastic Search: Search keyword
27. Elastic Search → Redactietool: Return matched keywords list
28. Redactietool → Redactietool: Add keyword to selected keywords in leerobject

### Save metadata

29. Redactietool → Redactietool: Construct sidecar for updating metadata
30. Redactietool → FTP Server: Transfer collateral to MH transfer area
31. Redactietool → FTP Server: Transfer sidecar XML to MH transfer area
32. Redactietool → MediaHaven: Update object with transformed metadata
33. MediaHaven → Redactietool: Display results in metadata edit form

---

## Ondertitels toevoegen

34. Redactietool → Redactietool: Redirect to subtitle upload page
35. Redactietool → MediaHaven: Get existing subtitle files using object request with same PID
36. MediaHaven → Redactietool: Return list of uploaded subtitles to show in upload page
37. Redactietool → Redactietool: Upload SRT file
38. Redactietool → Redactietool: Parse and convert SRT into WebVTT file
39. Redactietool → Redactietool: Redirect to preview page that shows local WebVTT in browser
40. Redactietool → Redactietool: Construct sidecar for updating subtitle file
41. Redactietool → FTP Server: Transfer WebVTT to MH transfer area
42. Redactietool → FTP Server: Transfer sidecar XML to MH transfer area
43. FTP Server → Redactietool: Display results of FTP upload response

---

## Logout flow

44. Redactietool → SAML server: Logout request
45. SAML server → Redactietool: Logout / remove session on all connected applications
46. Redactietool → Redactietool: Redirect to login screen





# General overview:

Below is a maintenance-oriented digest of what the meeting reveals about the **redactietool** architecture, with extra focus on **subtitle upload / update flows**.

## 1. What the redactietool is

The redactietool is essentially a **custom editorial interface on top of Mediahaven** for the **Archief voor Onderwijs / AVO** workflow. The key design constraint is that AVO does **not enrich the partners’ original archive objects directly**. Instead, content is first copied or clipped into AVO’s own Mediahaven tenant / “testbeeld”-style environment, and the redactietool edits metadata on that copy.

A typical workflow is:

```text
Partner item in Mediahaven
        ↓ export / copy / clip
AVO-owned item in Mediahaven tenant
        ↓ enter PID in redactietool
Redactietool fetches metadata + media preview
        ↓ editor updates selected fields
Updated metadata is saved back to Mediahaven
        ↓ AVO sync / publication flow picks it up
AVO site eventually publishes / exposes it
```

The tool starts from a **PID**. It fetches item data from Mediahaven, shows only the metadata fields that matter for AVO, lets editors modify a subset, and pushes changes back to Mediahaven. The Mediahaven item contains more metadata than the tool shows.

## 2. Functional modules

The interface has roughly these areas:

| Area                      | Purpose                                                                         | Backend / data source                                                  |
| ------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Basic metadata            | Title, series, dates, disclosure/publication-related fields, etc.               | Mostly Mediahaven                                                      |
| Media preview / keyframe  | Playback and start image selection                                              | Mediahaven player / Mediahaven keyframe functionality                  |
| Description for education | Rich text / HTML-ish editorial description used on AVO                          | Saved back to Mediahaven, later picked up by AVO                       |
| Production metadata       | Optional / future-oriented fields like production house, director, actors, etc. | Mediahaven fields, not heavily used                                    |
| Learning object metadata  | Onderwijsniveau, graad, thema’s, vakken, trefwoorden, etc.                      | Mix of Mediahaven, Knowledge Graph / SPARQL, Elasticsearch             |
| Publication status        | Marks item as eligible for sync / pickup                                        | Saved to Mediahaven; AVO still has its own publication step            |
| Subtitles                 | Upload, preview, confirm subtitle files                                         | Special flow involving SRT, VTT preview, XML sidecar, FTP / Mediahaven |

The meeting repeatedly frames the redactietool as “glue”: it connects Mediahaven, AVO metadata conventions, knowledge graph suggestions, keyword lookup, and subtitle upload. There was no existing architecture diagram; this was explicitly called out as something that would be useful to document.

## 3. Technical stack

From Walter’s handover:

```text
Backend: Python Flask
Frontend: mixed
  - server-rendered Jinja templates + vanilla JavaScript
  - Vue 2 for the more complex learning-object metadata UI
Rich text editor: Quill
Media preview subtitle player: Flowplayer
Deployment: Docker / OpenShift / Kubernetes-style environment
CI/CD: Jenkins mentioned
Auth: SAML / “Samuel” login
Config: environment variables, especially for Mediahaven, FTP, SPARQL, Elasticsearch
```

The older/simple sections are rendered with Flask/Jinja templates and enhanced with vanilla JavaScript. The more complex learning-object metadata section was built as a Vue 2 component because it needed multiselects, modals, suggestions, and dynamic filtering. The Vue app is not a full standalone SPA; it is embedded into the server-rendered page. It receives initial metadata by reading JSON injected into the page, partly because the Vue app itself does not handle SAML authentication.

A notable maintenance point: the app is old enough that Vue 2 and some Python/SAML dependencies should be reviewed. Walter suggested Vue 2 → Vue 3 should be feasible because the Vue portion is relatively small and has few dependencies, but the team still needs to decide whether upgrade/security hardening is part of the immediate scope or handled separately as recurrent lifecycle management.

## 4. Metadata data flows

The main metadata save path is:

```text
Redactietool
  → Mediahaven API
  → Mediahaven item metadata updated
  → AVO sync / reindex / publication process
  → AVO site
```

Walter described a `meta_mapping` layer that maps Mediahaven’s XML-ish / JSON-ish responses into the internal form model and back. This exists partly because Mediahaven moved APIs over time and because some features historically only worked through XML, not JSON.

For **learning object metadata**, the redactietool uses a SPARQL API / Knowledge Graph integration to fetch education levels, grades, themes, subjects, and relationships. The UI suggests values based on selected combinations, but editors can still deviate from suggestions. The details of that business logic are partly in the Knowledge Graph/SPARQL side and should be documented with Miel/Emiel.

For **trefwoorden / keywords**, Walter initially thought it might also be SPARQL, but then identified it as a separate Elasticsearch lookup. The selected keywords are saved back to Mediahaven and later end up in Elasticsearch again through the broader indexing flow.

## 5. Subtitle upload / update flow

This is the most interesting and most fragile part.

### Current functional process

Subtitles are uploaded through a separate subtitle area in the redactietool. Functionally, editors:

```text
1. Open subtitle section for an AVO item
2. Choose subtitle type: open or closed
3. Upload an SRT file
4. Preview subtitles on the video
5. Confirm upload
6. Subtitle becomes linked to the item
```

The tool distinguishes **open** and **closed** subtitles. In the discussion, closed captions are described as teletekst/accessibility-style subtitles that include things like speaker/sound context, while open subtitles are the regular subtitles users more commonly want to toggle.

The meeting notes a product limitation: although both open and closed files can technically be uploaded, using both is not currently very useful because the AVO player does not offer a good UX for choosing open, closed, or both together. The current workaround is sometimes to merge open and closed content, but that is imperfect because some users do not want closed-caption details.

### Preview mechanics

The redactietool accepts an **SRT** file, but for preview it converts SRT to **VTT**, because the browser/player preview uses VTT. The preview step uses **Flowplayer** to show the uploaded subtitles on the video before final confirmation.

So the preview pipeline is roughly:

```text
Uploaded SRT
   ↓
SRT → VTT conversion
   ↓
Flowplayer preview
   ↓
Editor confirms
```

### Upload mechanics to Mediahaven

Historically, subtitle upload could not be done cleanly through the newer Mediahaven JSON API. Walter says the Mediahaven V2 API existed, but the call needed for subtitles did not work with JSON at the time. Therefore the redactietool had to upload subtitle assets via **FTP**, together with an **XML sidecar** containing metadata such as PID/content partner/type information.

The flow is approximately:

```text
Editor uploads SRT in redactietool
        ↓
Redactietool validates / previews as VTT
        ↓
On confirm:
  - SRT asset is uploaded via FTP
  - XML sidecar is generated
  - sidecar links subtitle asset to Mediahaven item / media event
        ↓
Mediahaven ingests / associates subtitle
        ↓
AVO can use the subtitle after sync/publication flow
```

The exact current status is uncertain. A specific follow-up was recorded: ask **Maarten** or **Matthias Poppe** why FTP/XML was required, whether the Mediahaven API can now handle subtitle uploads properly, and if so, how the modern implementation should work.

### Why subtitles can only be uploaded after AVO publication

Functionally, Lander says subtitles can only be uploaded once the item is effectively published on AVO; they cannot currently be prepared earlier in the editorial process. That is painful because subtitles are sometimes needed to understand the item before publication.

The cause was **not definitively resolved** in the meeting. Walter strongly indicates the redactietool itself is probably **not** the component enforcing the limitation. The likely cause is somewhere in the Mediahaven/AVO publication/linking flow or the legacy FTP/XML sidecar ingestion path.

So for maintenance, treat this as an open architecture question:

```text
Is the “only after publication” constraint caused by:
  - AVO requiring a published item before subtitle association?
  - Mediahaven requiring a specific media event / item state?
  - The FTP/XML sidecar ingestion flow?
  - An old assumption in the redactietool UI?
```

Walter’s position: “not the redactietool”; the tool had to adapt to the constraints imposed by the external systems.

## 6. AI / generated metadata direction

The future feature request is to add a **“generate metadata”** flow from the redactietool, primarily for **speech-to-text transcription**, summaries, and chaptering. The motivation is clear: for long audio/video, manual description is extremely time-consuming, and transcript-based generation could reduce work from many hours to roughly review/edit time.

The desired UX is:

```text
Editor opens item in redactietool
   ↓
Clicks “generate metadata”
   ↓
System fetches media/audio from Mediahaven
   ↓
Optionally extracts audio from video
   ↓
Sends audio to Speechmatics or alternative service
   ↓
Receives transcript / summary / chapters
   ↓
Shows generated output in redactietool
   ↓
Human editor reviews and approves
```

Speechmatics is the current likely candidate because meemoo already has a framework agreement / project context around it, but the team wants to compare alternatives and align with broader meemoo AI/Hermes work.

A key architectural warning came up: generated content should not simply overwrite human-approved fields. The data model should distinguish **generated** vs **human verified** metadata.

## 7. Main risks / maintenance concerns

The biggest maintenance concerns I’d extract are:

1. **Subtitle upload is legacy/fragile.** It depends on FTP + XML sidecar because the API did not support the needed flow at the time. This should be revalidated against the current Mediahaven API.

2. **Architecture is under-documented.** There is useful code documentation, but no complete flow diagram of all systems, URLs, and data movement. The team explicitly asked for such a diagram.

3. **Mixed frontend architecture.** Server-rendered Flask/Jinja + vanilla JS + embedded Vue 2 is manageable, but future work should avoid making this split messier.

4. **Knowledge Graph logic is partly external/black-box.** Suggestions for educational metadata depend on SPARQL/Knowledge Graph rules that should be documented with the relevant owner.

5. **Security/dependency posture needs review.** The app is old, exposed outside VPN at least at the time of discussion, and uses older dependencies. Options discussed include upgrading dependencies, moving back behind VPN, or setting up recurrent lifecycle management.

6. **AI output needs provenance.** Generated metadata should be stored separately from verified editorial metadata, with human review and provenance/transparency.

## 8. Concrete follow-up questions

For the subtitle track, I would prioritize these:

1. **Can Mediahaven now upload subtitles through API instead of FTP/XML sidecar?**
   Owner suggested in meeting: Maarten / Matthias Poppe.

2. **Where exactly is the “only after AVO publication” constraint enforced?**
   Check AVO, Mediahaven item state/media event requirements, and sidecar ingestion.

3. **Can subtitles be attached earlier to the Mediahaven item, before AVO publication?**
   This would improve the editorial workflow substantially.

4. **Should the AVO player support three subtitle modes: open, closed, merged/both?**
   This is likely an AVO/player UX decision, not just a redactietool issue.

5. **If AI generates transcripts/SRTs, where do those live before approval?**
   Avoid writing generated text directly into the current human editorial fields.

6. **Should subtitle generation and metadata generation share the same AI pipeline?**
   Speech-to-text can feed both captions and summaries/chapters, but the data models and approval flows differ.

## 9. Suggested architecture target

A cleaner future architecture would look like this:

```text
Redactietool UI
  ├─ Metadata editor
  │   ├─ Mediahaven API for canonical item metadata
  │   ├─ Knowledge Graph/SPARQL for education metadata suggestions
  │   └─ Elasticsearch/API for keyword lookup
  │
  ├─ Subtitle manager
  │   ├─ Upload existing SRT/VTT
  │   ├─ Preview via player
  │   ├─ Store via current Mediahaven API, not FTP if possible
  │   └─ Track subtitle type: open / closed / merged
  │
  └─ AI assistant
      ├─ Fetch media/audio from Mediahaven
      ├─ Optional audio extraction
      ├─ Speechmatics or alternative STT
      ├─ Store generated transcript/summary/chapters separately
      └─ Human approval writes to canonical Mediahaven/AVO fields
```

The immediate maintenance move is to document the current reality first, especially the FTP/XML subtitle path, before replacing it.
