---
title: MediaHaven REST API v2
version: 26.1.163
source_url: https://archief.viaa.be/mediahaven-rest-api/v2/api-docs/index.html
generated_from:
  - mediahaven-api-docs.html
  - mediahaven-api-docs.md
notes: Cleaned for use in a .agents folder. Page navigation, scripts, and styling were removed; original section anchors were preserved where available.
---
# MediaHaven Rest API Manual {#mediahaven-rest-api-manual}

This documentation describes the v2 REST API for the MediaHaven platform.

You can find the [latest release notes](#release_notes) at the bottom.

## Test Environment {#test-environment}

To test the integration of your application we provide a test environment:

```http
https://integration.mediahaven.com/mediahaven-rest-api/
```

This setup can be reset or upgraded without notice, so keep in mind that your data will be lost and that the environment will be unavailable during 10 to 15 minutes

Following configuration settings can be used:

|  |  |
| --- | --- |
| Username | apikey |
| Password | apikey |
| IngestSpaceId | 5ebefe86-279c-4e19-857c-23ec0e975278 |
| DepartmentId | cc6ea4c0-c7e9-44e3-906e-8b689d95c8f2 |

## Authentication {#authentication}

All requests to the API need to be authenticated using OAuth2.0.

Using OAuth2.0 authentication you can access MediaHaven on behalf of your end users, without actually knowing and handling their password. This increases security a lot.
Your integration is also immune for potential password changes, which is also a big convenience improvement.

By using OAuth2.0 as authentication mechanism, users can log in using the same system they use to log in to MediaHaven.
SO if users can log in to MediaHaven using external authentication (SAML), they can also use this to log in to your extension.

This alleviates the need to create separate internal MediaHaven users next to their external authentication counterpart.

All information on the available grants, and how to apply for tokens can be found in the [OAuth2.0 Documentation](https://mediahaven.atlassian.net/wiki/display/CS/OAuth2.0).

## Content Negotiation {#content-negotiation}

By providing an accept header it is possible to retrieve responses from the webservice in JSON or XML format.

If you want to receive the answer in an xml format you can provide following header:

```http
Accept: application/xml
```

Currently we support:

- application/xml
- application/json

If no Accept header is specified the format of the response will be JSON.

## Creating / Uploading {#uploading}

To upload/create you make a POST request to the `records`-resource:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records
```

You can create objects in our system that correspond to a [physical file in storage](#uploading_file),
or [pure-metadata objects](#create_without_file).

### File upload {#uploading_file}

The file upload operation delivers a file to the MediaHaven application for processing.
The return value of the upload operation contains the metadata before processing the object.

We provide 3 options to upload a file to the system:

- [Direct upload](#direct_file_upload)
- [Upload from url](#url_file_upload)
- [Resumable upload](#resumable_file_upload)

#### Parameters

The following parameters are available for all upload methods

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| title | String | the title of the object that will be created | filename | yes |
| metadata | [Sidecar](#sidecar_format) | [(sidecar) metadata file](#metadata), json or xml, that you want to upload (always provide a content-type for this parameter!) |  | yes |
| autoPublish | Boolean | `Deprecated property, might be removed in the future. use publish instead` True if you want the file to be published automatically | false | no |
| publish | Boolean | Publish the file immediately after being created. | false | no |
| ingestSpaceId | String | ID of the ingest space in which the file has to be uploaded. Mutually exclusive with `zone` (must refer to ingest space of the [current user](#current_user)) |  | only when publish = false |
| zone | String | ID or the name of the zone in which the file has to be uploaded. Mutually exclusive with `ingestSpaceId`. |  | only when publish = false |
| externalId | String | the external Id of the object, must be unique |  | no |
| departmentId | String | the id of the department to which the file will be published (must refer to a group of the [current user](#current_user) where WriteRights = true.) |  | no |
| eventType | String | sub event type for audit logging |  | no |
| workflow | String | the workflow that should be started for processing this file. Specify ‘Ingest-1.0’ to use the legacy ingest, or ‘NO_WORKFLOW’ to skip workflow. | depends on the default record type | no |
| recordType | String | Type of the created record. The list of possible values can be requested via [record types](#record_types) | default record type as specified by [/record-types](#record_type_object) | no |
| adoption.parentRecordId | String | Provide the `RecordId` of the record to be parent whose metadata is inherited as defined by the [field definitions](#field_definitions) | user preference DEFAULT_CLASSIFICATION (if not recordType Classification) | no |
| adoption.forcedInheritance | Boolean | If true, overwrite inheriting metadata fields with the value from the parent for this record and its (grand)children, even if the record already has a value for that field | false | no |
| adoption.candidate | Boolean | If true, only inherit metadata but without becoming a permanent child of the parent record | false |  |
| adoption.profileStrategy | Enum (OVERWRITE,MERGE) | The strategy used to update the profiles (MERGE = keep existing profiles and add new) (OVERWRITE = remove old profiles) | MERGE |  |
| previewRecordId | String (hexadecimal string of 64 characters ) | Assign another record as preview |  | no |
| childOrderFields | String[] | DottedKey of the field that should be sorted on (referenced field must be Sortable), and optionally the direction (asc, up or desc, down) |  | no |
| fileRecord.metadata | [Sidecar](#sidecar_format) | `Advanced feature, usage is discouraged for most users.` [(sidecar) metadata file](#metadata), json or xml, that you want to use for the generated file record. (always provide a content-type for this parameter!) |  | no |
| fileRecord.creation | Enum (Direct,Delayed) | `Advanced feature, usage is discouraged for most users.` This option determines whether the file record (representation) is creation in the initial create call, or whether it will be created later. Only applicable for data records. | Default | no |
| priority | Enum (High, Normal, Low, Background) | Priority for the processing of the uploaded file. Setting this property requires the function `ADMIN_BACKEND_SERVICES` | depends on workflow | no |
| organisationId | Integer | When provided the record should be created for the organisation with this ID instead. Requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`. Can not be combined with organisationExternalId. | N/A | no |
| organisationExternalId | String | When provided the record should be created for the organisation with this external ID instead. Requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`. Can not be combined with organisationId. | N/A | no |
| ingestConfigurationId | String | When provided, the record is ingested using the [ingest configuration](#ingest_configuration) with this ID. | N/A | no |

> For the metadata you must provide a
> content-type to the FormData (application/json or application/xml) otherwise we will not process the metadata!
>
> By default, the title of the object is set to the filename of the uploaded file, you can override this using
> the `title`
> -parameter.
>
> Note: Whether a metadata field is editable depends on the active Classification profiles for a record. See [Classification profile field properties](#profile_field_classification_properties) for more info.
>
> Note: Zone must refer to a zone of the [current user](#current_user), or the user must have the user function ADMIN_ZONES and the zone must belong to the organisation of the [current user](#current_user).

#### Specifying the organisation ID

Specifying the organisation ID is a useful property for integrators creating records for multiple organisations using
the
same API user. The following restrictions apply

- The user must have the function `ADMIN_EDIT_ALL_ORGANISATIONS`
- The target organisation MUST NOT be a system organisation (e.g. _default or monitor)
- The permissions should be either be explicitly provided or there is a parent record to inherit the permissions from

#### Response

- `201` Created: [Record](#record-object)
- `404` Not found
    - adoption.parentRecordId or previewRecordId can’t be found
    - childOrderFields references a field that doesn’t exist
    - ingestConfigurationId can’t be found
- `400` Bad request: [error result](#error)
    - adoption.parentRecordId or previewRecordId contain an invalid record id
    - childOrderFields contains a DottedKey that is not Sortable
    - fileRecord.metadata is used for a record type that does not have a separate file record
- `403` Forbidden: [error result](#error)
- `409` Conflict: [error result](#error)
    - When the file is already present within your organisation
    - When violating
      the [record tree logic](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2291466251/Record+Tree)
    - When previewRecordId contains a record without valid browses. This means the BrowseStatus of the preview record is
      not equal to ‘Completed’.

#### Authorization functions

- Any authenticated user can access this resource
- PUBLISH_RIGHTS is needed if autoPublish = true or type = `Processing` (unless the RecordType is a helper recordType,
  like ‘ThesaurusSuggestion’)

#### Direct upload {#direct_file_upload}

Direct upload requires the content type `multipart/form-data` and the additional parameter `file`.

##### Parameters

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| file | multipart/file | the file that you wish to upload |  | yes |

Attach the file you want to upload as FormData using the `file`-parameter.

#### Upload from url {#url_file_upload}

Upload from url requires the additional parameter `fileUrl`.

This url should be accessible for the system, have a valid SSL certificate (if served over https) and should
support `HEAD`-requests.

> Warning: the URL must adhere to <https://www.rfc-editor.org/rfc/rfc1630>, in particular unsafe characters
> such as **spaces**, control characters, some characters whose ASCII code is used differently in
> different national character variant 7 bit sets, and all 8bit characters beyond DEL (7F hex) of
> the ISO Latin-1 set, shall **not be used unencoded**
>
> Redirects and `429` (Too many requests) are supported

##### Parameters

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| fileUrl | String (url) | the url of the file you wish to upload (mutually exclusive with file) |  | yes |

#### Response

The response can give some additional errors

- `400` Bad request: [error result](#error)
    - The url is invalid
    - The request to the url returned a status other than `2**` or `429`
- `429` The request to the url returned a too many requests error: [error result](#error)

#### Resumable upload {#resumable_file_upload}

Resumable upload allows you to upload the file after creation of the record.

This type of upload requires the additional parameters found below

The record will get the status `Uploading`.

##### Parameters

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| fileUpload.fileSize | Integer | The size in bytes of the file you want to upload |  | yes |
| fileUpload.filename | String | The original filename |  | yes |
| fileUpload.checksum | String | The checksum (MD5) of the file you want to upload |  | no |

After creation you can use the [Resumable upload api](#resumable_upload) to create a session and upload the file.

### Workflow {#workflow}

For advanced usage it’s possible to start a specific workflow for processing the file.

### Attaching sidecar metadata {#attaching_sidecar}

It is possible to provide a sidecar json/xml containing metadata using the `metadata`-parameter. This file must be in
the right format. Refer to [Sidecar metadata format](#metadata) for more specifics. The sidecar metadata has preference
over the supplied parameters. So for example a `title` defined in the sidecar XML will override a `title` defined as
parameter.

It is also possible to use such a sidecar metadata file to perform [metadata updates](#edit_field_XML) at a later stage.

### MD5-checksum validation {#md5_checksum_validation}

To ensure the integrity of your files, it is possible to supply a precalculated MD5-hash when uploading them to our
servers. We will then verify if the MD5 matches the uploaded file, and fail early if it doesn’t. This will ensure that
the files will not get corrupted during network transport.

The MD5 attribute can only be added using the metadata parameter. Refer to [Sidecar metadata](#metadata) for more
specifics.

### Without file {#create_without_file}

Valid content type when creating a record without file are `multipart/form-data`, `application/xml`
and `application/json`. Please note that if you wish to use [Sidecar XML](#sidecar_format), you’ll need to use
the `multipart/form-data` content type.

To create a pure-metadata object via `multipart/form-data` the strategy is the same as when uploading a file: make a
POST request to the `records`-resource, only now you don’t supply the `file` parameter. The request can also be sent
with Content-Type `application/json` or `application/xml` if you provide the metadata inline instead of attached file

We can distinguish 3 types of pure-metadata objects in our system:

- metadataonly
- set
- collection

We have another type object which initially starts as pure-metadata object, but in a later step acquires its physical
asset.

- processing

Everyone of these objects can have metadata like regular objects in our system. The set and collection objects (or ‘
ensembles’) are a bit different in that they represent a grouping of other objects.

Because the object-creation system infers the object title and type from the `file` parameter, which is not present,
this information has to be provided explicitly.

We repeat the table above, but now specifically for when the `file` parameter is *not* provided. The `workflow` parameter
is not applicable for records without a file.

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| title | String | the title of the object that will be created |  | yes |
| metadata | [Sidecar](#sidecar_format) | The [(sidecar) metadata file](#metadata), json or xml, that you want to upload. |  | no |
| type | Enum (`set`, `collection`, `processing`, `metadataonly`, `fragment`) | the type of object you want to create | metadataonly | no |
| autoPublish | Boolean | `Deprecated property, might be removed in the future. use publish instead` True if you want the file to be published automatically | false | no |
| publish | Boolean | Publish the file immediately after being created. | false | no |
| ingestSpaceId | String | The id of the ingestspace in which the file has to be uploaded. (must refer to ingest space of the [current user](#current_user)) |  | only when publish = false |
| externalId | String | The external Id of the object, must be unique |  | no |
| departmentId | String | the id of the department to which the file will be published (must refer to a group of the [current user](#current_user) where WriteRights = true.) |  | no |
| eventType | String | sub event type for audit logging |  | no |
| recordType | String | Type of the created record. The list of possible values is configured on the [field definition](#field_definitions) with key `RecordType`. | Record | no |
| adoption.parentRecordId | String | Provide the `RecordId` of the record to be parent whose metadata is inherited as defined by the [field definitions](#field_definitions) | user preference DEFAULT_CLASSIFICATION (if not recordType Classification) | no |
| adoption.forcedInheritance | Boolean | If true, overwrite inheriting metadata fields with the value from the parent for this record and its (grand)children, even if the record already has a value for that field | false | no |
| adoption.candidate | Boolean | If true, only inherit metadata but without becoming a permanent child of the parent record | false | no |
| adoption.profileStrategy | Enum (OVERWRITE,MERGE) | The strategy used to update the profiles (MERGE = keep existing profiles and add new) (OVERWRITE = remove old profiles) | MERGE |  |
| fragment.parentRecordId | String | `Deprecated` The `RecordId` of the record for which you are creating the fragment |  | only when type = `fragment` |
| fragment.fragmentStartFrames | Number | `Deprecated` Fragment in-point in frames, relative to parent |  | See [Fragments](#fragments) |
| fragment.fragmentEndFrames | Number | `Deprecated` Fragment out-point in frames, relative to parent |  | See [Fragments](#fragments) |
| fragment.fragmentStartTimeCode | String | `Deprecated` TimeCode of fragment in-point, relative to parent |  | See [Fragments](#fragments) |
| fragment.fragmentEndTimeCode | String | `Deprecated` TimeCode of fragment out-point, relative to parent |  | See [Fragments](#fragments) |
| previewRecordId | String (hexadecimal string of 64 characters ) | Assign another record as preview |  | no |
| childOrderFields | String[] | DottedKey of the field that should be sorted on (referenced field must be Sortable), and optionally the direction (asc, up or desc, down) e.g. to sort on title: childOrderFields=Descriptive.Title,asc |  | no |
| fileRecord.metadata | [Sidecar](#sidecar_format) | `Advanced feature, usage is discouraged for most users.` [(sidecar) metadata file](#metadata), json or xml, that you want to use for the generated file record (representation. Always provide a content-type for this parameter! |  | no |
| fileRecord.creation | Enum (Direct,Delayed) | `Advanced feature, usage is discouraged for most users.` This option determines whether the file record (representation) is creation in the initial create call, or whether it will be created later. Only applicable for data records. | Default | no |
| organisationId | Integer | When provided the record should be created for the organisation with this ID instead. Requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`. Can not be combined with organisationExternalId. | N/A | no |
| organisationExternalId | String | When provided the record should be created for the organisation with this external ID instead. Requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`. Can not be combined with organisationId. | N/A | no |
| ingestConfigurationId | String | When provided, the record is ingested using the [ingest configuration](#ingest_configuration) with this ID. | N/A | no |

> Note: Whether a metadata field is editable depends on the active Classification profiles for a record. See [Classification profile field properties](#profile_field_classification_properties) for more info.
> Note: Creating fragments via this endpoint is deprecated, use [create fragment](#fragments_post) instead.

#### Json object structure {#record-create-object}

```json
{
  "Title": "My title",
  "Metadata": {
    "Descriptive": {
      "Title": "My title"
    }
  },
  "Publish": false,
  "IngestSpaceId": "5ebefe86-279c-4e19-857c-23ec0e975278",
  "ExternalId": "external-identifier",
  "Type": "metadataonly",
  "EventType": "Create",
  "RecordType": "Record",
  "Adoption": {
    "ParentRecordId": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
    "ForcedInheritance": false,
    "Candidate": false,
    "ProfileStrategy": "OVERWRITE"
  },
  "PreviewRecordId": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
  "ChildOrderFields": {
    "Field": [
      {
        "DottedKey": "Descriptive.Title",
        "Direction": "asc"
      }
    ]
  },
  "OrganisationId": 156,
  "IngestConfigurationId": "6e222000-0000-0000-0000-000000000000"
}
```

#### XML object structure {#record-create-object-xml}

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CreateRecord>
    <Title>My title</Title>
    <Metadata>
        <mhs:Sidecar xmlns:mhs="https://zeticon.mediahaven.com/metadata/19.2/mhs/"
                     xmlns:mh="https://zeticon.mediahaven.com/metadata/19.2/mh/" version="19.2">
            <mhs:Descriptive>
                <mh:Title>My Title</mh:Title>
            </mhs:Descriptive>
        </mhs:Sidecar>
    </Metadata>
    <Publish>true</Publish>
    <IngestSpaceId>5ebefe86-279c-4e19-857c-23ec0e975278</IngestSpaceId>
    <ExternalId>external-identifier</ExternalId>
    <Type>metadataonly</Type>
    <EventType>Create</EventType>
    <RecordType>Record</RecordType>
    <Adoption>
        <ParentRecordId>c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1</ParentRecordId>
        <ForcedInheritance>false</ForcedInheritance>
        <Candidate>false</Candidate>
        <ProfileStrategy>OVERWRITE</ProfileStrategy>
    </Adoption>
    <PreviewRecordId>c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1</PreviewRecordId>
    <ChildOrderFields>
        <Field>
            <DottedKey>Descriptive.Title</DottedKey>
            <Direction>asc</Direction>
        </Field>
    </ChildOrderFields>
    <OrganisationId>134</OrganisationId>
</CreateRecord>
```

#### Response

- `201` Created: [Record](#record-object)
- `404` Not found
    - adoption.parentRecordId or PreviewRecordId can’t be found
    - childOrderFields references a field that doesn’t exist
    - ingestConfigurationId can’t be found
- `400` Bad request: [error result](#error)
    - adoption.parentRecordId or previewRecordId contain an invalid record id
    - childOrderFields contains a DottedKey that is not Sortable
- `403` Forbidden: [error result](#error)
- `409` Conflict: [error result](#error_duplicate)
    - When the file is already present within your organisation (checksum or external id)
    - When violating
      the [record tree logic](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2291466251/Record+Tree)
    - When previewRecordId contains a record without valid browses. This means the BrowseStatus of the preview record is
      not equal to ‘Completed’.

#### Authorization functions

- PUBLISH_RIGHTS is needed if autoPublish = true or type = `Processing` (unless the RecordType is a helper recordType,
  like ‘ThesaurusSuggestion’)

### Processing type {#processing_type}

Processing is a special type that allows you to create an object for a file you plan to upload in the future (via ftp or
another way). You are required to include the parameter metadata which must contain the technical fields FileSize and
Md5.

### Fragments {#fragments}

Fragments are specialised sub-objects with particular start and end coordinates, typically smaller than the entire object.
Fragments will share the RecordId with their parent, but differ in FragmentId, type and most metadata.
More details can be found [here](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/4668391481/Fragments).

To create a pure fragment you can use the [create fragment](#fragments_post) endpoint.

Although it is not recommended, you can still create fragments via the [create without file](#create_without_file) endpoint.
You can provide a fragment object with type = `fragment` and with the (relative) in- and out-points provided as arguments.
You can choose to either supply the boundaries on a Frame-basis or on a TimeCode-basis. Formats may not be mixed.

Example:

```json
{
  "Title": "My title",
  "Metadata": {
    "Dynamic": {
      "MyField": "MyValue"
    }
  },
  "Type": "fragment",
  "Fragment": {
    "ParentRecordId": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
    "FragmentStartTimeCode": "00:01:00.000",
    "FragmentEndTimeCode": "00:02:00.000"
  }
}
```

The specific fragment type will be resolved based on the parent record.
Note that for these records adoption currently is not supported.

### Zones & Ingest Spaces {#publish_automatically}

Records are uploaded to either Zones or Ingest Spaces. Zones are specialized ingest spaces described
here [in detail](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/3217850450/Zones).

### Publishing automatically {#publish_automatically}

By default, files are uploaded to an Ingest Space or Zone. As such you will have to supply the ingestSpaceId / zoneId to
where the object must be uploaded. The IDs of the ingest spaces / zones accessible to the user can be retrieved using
the [User endpoint](#user-resource).

In order to make the items publicly available, a manual “Publish” action is required.

If your user has the PUBLISH_RIGHTS userfunction, it is however possible to immediately publish the uploaded objects.
For this, the ID of the department to which the objects will be published can be provided if so desired and it will be
stored in the field DepartmentId. It can be defined as FormData parameter `departmentId` or as the JSON
field `DepartmentId`. The automatic publishing can be turned on by setting the FormData parameter `publish` or the JSON
field `Publish` to `true`.

For certain RecordTypes, the PUBLISH_RIGHTS userfunction is not required. E.g. to create a ‘ThesaurusSuggestion’.

## Resumable upload {#resumable_upload}

Resumable upload allows you to upload large files by splitting them in multiple chunks.

For implementation this API follows the rfc
at <https://www.ietf.org/archive/id/draft-ietf-httpbis-resumable-upload-04.html>

This corresponds to `Upload-draft-interop-version` = `6`

#### Starting a resumable upload {#resumable_upload_start}

> Note: Only for a record with status `Uploading` a resumable upload can be started.

Starting a resumable upload is done by sending a `POST` request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/uploads
```

With the following headers

| Header name | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Upload-Complete | [Boolean](https://httpwg.org/specs/rfc8941.html#ser-boolean) | Whether the upload is complete or not |  | Yes |
| Upload-Draft-Interop-Version | Integer | Version of the rfc draft, must be `6` |  | Yes |
| Content-Length | Integer | Size of uploaded chunk |  | Yes if you provide the first part |
| Content-Digest | String | MD5 checksum of the uploaded chunk |  | No |

And the following parameters:

| Parameters | Type | Description | Required |
| --- | --- | --- | --- |
| recordId | String | The recordId for which to start the upload | Yes |

The first part or the full part of the upload can be included as body.

Users can provide a `Content-Digest` header with the MD5 checksum of the uploaded chunk. This will be validated when
received.

When the upload is created the `Location` header in the response contains the target url for uploading the parts.

##### Response

- `200` Resumable upload is done
- `201` Resumable upload is created
- `404` The record does not exist
- `400` Invalid request
- `403` Resumable upload is not available or not allowed

#### Example response headers

```
Upload-Complete: ?0
Upload-Offset: 0
Upload-Limit: max-size=356172, max-append-size=356172, min-append-size=356172
Location: https://integration.mediahaven.com/mediahaven-rest-api/v2/uploads/8a14fac9d6d743ca92999ea0e1957947edbda685f0ca4ea5940a4aab2485ad8f?session=<SECRET>
```

#### Upload chunk {#resumable_upload_chunk}

Uploading a chunk is done by sending a `PATCH` request to the url receive from `Location` during creation

```http
https://archief.viaa.be/mediahaven-rest-api/v2/uploads/:sessionid
```

> Note: Parallel upload is not supported for the same ID

With the following headers:

| Header name | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Upload-Offset | Integer | The offset (in bytes) of the next chunk |  | Yes |
| Upload-Complete | [Boolean](https://httpwg.org/specs/rfc8941.html#ser-boolean) | Whether the upload is complete with this chunk or not |  | Yes |
| Upload-Draft-Interop-Version | Integer | Version of the rfc draft, must be `6` |  | Yes |
| Content-Length | Integer | Size of the chunk |  | Yes |
| Content-Digest | String | MD5 checksum of the uploaded chunk |  | No |
| Content-Type | String | Must be `application/partial-upload` |  | Yes |

The file chunk can be included as body (if no body is provided and `Upload-Complete` is true the upload will be
considered done)

Users can provide a `Content-Digest` header with the MD5 checksum of the uploaded chunk. This will be validated when
received.

###### Response

- `200` Resumable upload is done
- `201` Resumable upload continues [upload offset headers](#upload_offset_object)
- `400` Invalid request
- `404` The record does not exist
- `403` Resumable upload is not available or not allowed
- `409` Invalid offset [upload offset invalid](#upload_offset_invalid_object)

#### Offset retrieval {#resumable_upload_offset_retrieval}

Requesting the current offset can be done by sending a `HEAD` request to url received from `Location` during creation

```http
https://archief.viaa.be/mediahaven-rest-api/v2/uploads/:sessionid
```

##### Response

- `204` Valid upload uri [upload offset headers](#upload_offset_object)
- `400` Invalid request
- `404` The record or upload does not exist
- `403` Resumable upload is not available or not allowed

#### Example response headers

```
Upload-Complete: ?0
Upload-Offset: 0
Upload-Limit: max-size=356172, max-append-size=356172, min-append-size=356172
```

#### Cancel upload {#resumable_upload_cancel}

Cancelling an upload can be done by sending a `DELETE` request to url received from `Location` during creation

```http
https://archief.viaa.be/mediahaven-rest-api/v2/uploads/:sessionid
```

##### Response

- `204` Upload has been cancelled
- `400` Invalid request
- `404` The upload does not exist
- `403` Resumable upload is not available or not allowed

### Upload limit structure {#upload_limit_object}

| Property | Type | Description |
| --- | --- | --- |
| max-size | Integer | Maximum size for the total upload, counted in bytes (depends on the filesize given during record creation) |
| max-append-size | Integer | The maximum size of a chunk |
| min-append-size | Integer | The minimum size of a chunk |
| expires | Integer | Seconds until this object is destroyed |

#### Example response headers

```http
Upload-Limit: max-size=112756226, max-append-size=10485760, min-append-size=10485760
```

### Upload record options structure {#upload_record_options}

| Header name | Type | Description |
| --- | --- | --- |
| Upload-Limit | [upload limit object](#upload_limit_object) | Upload limits information |

### Upload offset structure {#upload_offset_object}

| Header name | Type | Description |
| --- | --- | --- |
| Upload-Offset | Integer | The offset (in bytes) of the next chunk |
| Upload-Complete | [Boolean](https://httpwg.org/specs/rfc8941.html#ser-boolean): ?0 or ?1 | Whether the upload is complete or not |
| Upload-Limit | [upload limit object](#upload_limit_object) | Upload limits information |

#### Example response headers

```
Upload-Limit: max-size=112756226, max-append-size=10485760, min-append-size=10485760
Upload-Offset: 0
Upload-Complete: ?0
```

### Upload offset invalid structure {#upload_offset_invalid_object}

| Property name | Type | Description |
| --- | --- | --- |
| Expected-Offset | Integer | The offset (in bytes) of the next chunk |
| Provided-Offset | Integer | The offset (in bytes) provided |

## Record types {#record_types}

### Description {#record_types_description}

Record types determine the types you can create via the [Records endpoint](#uploading).
Each type has its specific requirements and type of data.

With this endpoint you can request the record types allowed within the organisation.

### Getting all record types {#record_types_get_all}

Retrieve a [Page](#page) of [Record types](#record_type_object) using a `GET` request:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/record-types
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| structures | The structures to filter by |  |
| organisationId | The organisation to fetch the record types for. Requires ‘ADMIN_BACKEND_SERVICES’ to change | The organisation of the user |
| applyScheme | Should the organisation’ scheme be applied. Requires ‘ADMIN_BACKEND_SERVICES’ to change | True |

#### Response

- `200` A [Page](#page) of [Record types](#record_type_object)

#### Authorization functions

- Any authenticated user can access this resource

### Creating a record type {#record_type_create}

A record type can be created by performing a `POST`-request
with [Record type](#create_update_record_type_object) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/record-types
```

#### Response

- `201` The created [Record type](#create_update_record_type_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function

#### Authorization functions

- Using this endpoint requires the `ADMIN_BACKEND_SERVICES` function.

### Update a record type {#record_type_update}

Updating a record type can be done by performing a `PUT`-request
with [Record type](#create_update_record_type_object) to the following endpoint.

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/record-types/:Name
```

#### Response

- `200` Ok. Body: Updated [Record type](#create_update_record_type_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function

#### Authorization functions

- Using this endpoint requires the `ADMIN_BACKEND_SERVICES` function.

### Record type object structure {#create_update_record_type_object}

| Property | Type | Description | ReadOnly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Name | String | The record type name | Yes, after creation |  | Yes |
| Workflow | String | The default workflow | No | Empty |  |
| Structure | Enum (Intellectual,DataFlat,Data,Representation,Classification) | The structure | Yes, after creation |  | Yes |
| InformationPackage | Enum (Aip,Sip,Cip,Dip) | The information package | Yes, after creation |  | Yes |
| DeletionPolicy | Enum (None, RequireNoChildren, AdoptChildrenToParent, Cascade) | The behavior on deletion | No |  | Yes |
| PublicationPolicy | Enum[] (RequirePublishedParent, Cascade) | The behavior on publication | No | Empty |  |
| PublicationWorkflow | String | The workflow that will be started on publication | No | Empty |  |
| Permissions > Inheritance | boolean | Are permissions inherited to children | No | true |  |
| Permissions > InheritanceRules | Enum[] (AddOrganisationGroupType, AddDefaultOrganisationGroups) | Permission inheritance rules | No | Empty |  |
| DefaultRecordStatus | Enum | Default record status | No | If Structure = ‘Intellectual’ => Draft.Valid, otherwise ‘New’ |  |
| SubTypes | String[] | Subtypes | You are only allowed to add sub types, not allowed to remove them | Empty |  |
| CanPublishOnCreate | boolean | Can publish on create | No | false |  |
| MediaTypeSupport | boolean | Whether this record type supports media types | No | false |  |
| FragmentSupport | boolean | Whether this record type supports fragments | No | false |  |
| Labels | Label[] | Labels for the record type | No |  |  |
| Labels > Lang | String | The locale for the label | No |  |  |
| Labels > Label | String | The label for the given locale, if not defined, a fallback will be used | No |  |  |
| Publish | boolean | When doing bulk calls this can be used to avoid having to wait after each change | Yes | true |

> Note: `Labels` contains translations for each supported locale. If no translation is defined for a specific locale, a fallback will be used, namely the first non-empty value from the following list:
>  - The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
>  - The translation for the ‘overall’ default locale `en_US`
>  - Empty value

### Record type object with scheme structure {#record_type_object}

| Property | Type | Description |
| --- | --- | --- |
| Name | String | The name of the record type |
| Structure | Enum (Intellectual,DataFlat,Data,Representation,Classification) | The structure of the record type |
| Workflow | String | the workflow that will be started on creation |
| PublicationWorkflow | String | the workflow that will be started on publication |
| InformationPackage | Enum (Aip,Sip,Cip,Dip) | The type of information package this record defines |
| DeletionPolicy | Enum (None, RequireNoChildren, AdoptChildrenToParent, Cascade) | The behavior on deletion |
| PublicationPolicy | Enum[] (RequirePublishedParent, Cascade) | The behavior on publication. Requires explicit `Publish=true` when POSTing the record. |
| DefaultRecordType | boolean | Whether this is the default record type, exactly 1 record type is the default |
| DefaultRecordStatus | [RecordStatuses](#record_statuses) | The initial record status upon creation. |
| DefaultRecordStatus | [RecordStatuses](#record_statuses) | The initial record status upon creation. |
| Permissions > Inheritance | boolean | Are permissions inherited to children |
| Permissions > InheritanceRules | Enum[] (AddOrganisationGroupType, AddDefaultOrganisationGroups) | Permission inheritance rules |
| SubTypes | String[] ( Sub type name ) | The possible sub types (ex. if Name is Media and SubType is Video, the full type is Media.Type) |
| MediaTypeSupport | boolean | Whether this record type supports media types | No | false |  |
| FragmentSupport | boolean | Whether this record type supports fragments | No | false |  |
| AllowedChildren | String[] ( Record type name ) | The allowed children of this record type |
| Strict | boolean | Is the allowed children enforced |
| Scheme > Id | String | The internal id of the scheme |
| Scheme > Name | String | The name of the scheme |
| Scheme > ExternalId | String | The external reference of this scheme |
| Scheme > OrganisationId | Integer | The organisation this scheme is part of |
| Labels | Label[] | Labels for the record type |
| Labels.Lang | String | The locale for the label |
| Labels.Value | String | The label for the given locale, if not defined, a fallback will be used |
| Active | Boolean | Whether the RecordType is active. New records of this type can be created or uploaded only if active; existing records cannot be converted to it |

*Conceptual information packages are by default not exposed in the search engine*

> Note: `Labels` contains translations for each supported locale. If no translation is defined for a specific locale, a fallback will be used, namely the first non-empty value from the following list:
> - The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
> - The translation for the ‘overall’ default locale `en_US`
> - Empty value

### Structures {#record_types_structures}

We have 4 structures:

- **Intellectual**: A single record is created which contains only metadata a preview uri (Browse). Can only describe
  metadata records (a file is forbidden for uploading)
- **Data**: Multiple records are created (metadata record, original, preservation and access digital files) in a tree
  structure. Can only describe file based records (a file is required for uploading)
- **Data flat**: A single record is created which contains metadata a preview uri (Browse), no extra validation checks.
  Can contain metadata and file
- **Representation**: A digital representation of a `Data` structure record.

### Information packages {#information_packages}

We have 4 type of packages:

- **Archival (`AIP`)**: AIP is an information package that is used to transmit archival objects into a digital archival
  system, store the objects within the system, and transmit objects from the system. An AIP contains both metadata that
  describes the structure and content of an archived essence and the actual essence itself. It consists of multiple data
  files that hold either a logically or physically packaged entity.
- **Submission (`SIP`)**: SIP is an information package used for ingestion of multiple files and contains metadata about
  those files. After ingestion this record is removed.
- **Conceptual (`CIP`)**: CIP is an information package used for records that structure and link objects in the archive
  system
- **Dissemination (`DIP`)**: DIP is an information package received by the consumer in response to a request for
  content, or an order.

### Record statuses {#record_statuses}

Record status list (installation dependent).

## Record Scheme {#record_types}

### Description {#record_scheme_description}

Record scheme is the scheme management api for the [Record types](#record_types) allowed within a specific organisation.

With this endpoint you can request the record types allowed within the organisation.

### Get scheme {#record_scheme_get}

Retrieve a [Scheme](#record_scheme_object) using a `GET` request:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/{id}/record-scheme
```

#### Response

- `200` A [Record scheme](#record_scheme_object)

#### Authorization functions

- Any authenticated user can access this resource

### Updating a scheme {#record_scheme_update}

A record scheme can be updated by performing a `POST`-request
with [Record scheme](#record_scheme_object) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/{id}/record-scheme
```

#### Response

- `201` The created [Record scheme](#record_scheme_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function

#### Authorization functions

- Using this endpoint requires the `ADMIN_BACKEND_SERVICES` function.

### Record type object with scheme structure {#record_scheme_object}

| Property | Type | Description |
| --- | --- | --- |
| Name | String | The name of the record type |
| OrganisationId | Integer | Id of the organisation |
| DefaultRecordType | String | Default record type when a new record is created |
| ExternalId | String | ExternalId for this scheme |
| Types > RecordType | String | Record type allowed in this scheme |
| Types > AllowedChildren | String[] | Children allowed for this record type |
| Types > Strict | Boolean | Should the AllowedChildren be strictly validated or are they just hints |
| Types > Active | Boolean | Whether the RecordType is active. New records of this type can be created or uploaded only if active; existing records cannot be converted to it |

### Get default scheme {#record_scheme_get_default}

Retrieve a [Scheme](#record_scheme_object) using a `GET` request:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/record-schemes/default
```

#### Response

- `200` A [Record scheme](#record_scheme_object)

#### Authorization functions

- Using this endpoint requires the `ADMIN_BACKEND_SERVICES` function.

### Update default scheme {#record_scheme_update_default}

The default scheme can be updated by performing a `POST`-request
with [Record scheme](#record_scheme_object) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/record-schemes/default
```

#### Response

- `200` A [Record scheme](#record_scheme_object)

#### Authorization functions

- Using this endpoint requires the `ADMIN_BACKEND_SERVICES` function.

## Editing metadata {#edit_metadata}

### Editing a record {#edit_field_XML}

The structure of the [sidecar](#metadata) is the same as you would use when [uploading](#uploading).

The metadata supplied this way will be combined with the existing metadata. Simple-text fields (e.g. `title`
, `description`) will be overwritten with the new value, while list fields (e.g. `keywords`, `authors`) will be merged.

Since the operation has effect on the whole fragment, the POST request has to be made to the fragment URI:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id
```

Following content types are supported:

- `application/json`
- `multipart/form-data`
- `application/xml`

Please note that if you wish to use [Sidecar XML](#sidecar_format), you’ll need to use the `multipart/form-data` content
type.

#### Merge strategies

It’s possible to apply merge strategies to top-level fields. Following strategies are available:

- KEEP
- MERGE
- OVERWRITE
- SUBTRACT

For a more detailed explanation,
consult <https://mediahaven.atlassian.net/wiki/spaces/CS/pages/722567181/Metadata+Strategy>

#### FormData parameters {#edit_formdata_parameters}

| FormData parameter | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| metadata | [Sidecar](#sidecar_format) | The [(sidecar) metadata file](#metadata), json or xml, that you want to upload. (always provide content-type for this parameter) |  | yes |
| reason | String | The reason the record was updated. |  | no |
| eventType | String | Sub event type for audit logging |  | no |
| publish | Boolean | Publish the record. | false | no |
| adoption.parentRecordId | String | Provide the `RecordId` of the record to be parent whose metadata is inherited as defined by the [field definitions](#field_definitions). |  | no |
| adoption.forcedInheritance | Boolean | If true, overwrite inheriting metadata fields with the value from the parent for this record and its (grand)children, even if the record already has a value for that field. | false | no |
| adoption.candidate | Boolean | If true, only inherit metadata but without becoming a permanent child of the parent record. | false | no |
| adoption.profileStrategy | Enum (OVERWRITE, MERGE) | The strategy used to update the profiles (MERGE = keep existing profiles and add new) (OVERWRITE = remove old profiles) | MERGE | no |
| previewRecordId | String (hexadecimal string of 64 characters ) | Assign another record as preview for the current record |  | no |
| childOrderFields | String[] | DottedKey of the field that should be sorted on (referenced field must be Sortable), and optionally the direction (asc, up or desc, down) e.g. to sort on title: childOrderFields=Descriptive.Title,asc |  | no |

For more info on childOrderFields, see also [child sorting](#default_child_sorting)
and [sorting results](#sorting_results).

### Version Management {#mediahaven-rest-api-manual-editing-metadata-version-management}

When creating or updating records, the returned metadata contains the premis event ID of the action

- In the metadata field `Internal.LastUpdatePremisEventId`, e.g., `14096704`
- As the HTTPS header `ETag` in the form `W/"<Internal.LastUpdatePremisEventId>"`, e.g. `W/"14096704"`

When updating a record, it is now possible to provide the last update premis event ID of the retrieved record, using the
HTTPS header `If-Match` in the form of `W/"<Internal.LastUpdatePremisEventId>"`, e.g. `W/"14096704"`. If a metadata
collision
is detected, the HTTPS status `412 Precondition failed` will be raised.

See [Version Conflict Detection](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/5070487629/Version+Conflict+Detection)
for additional details.

#### Record update JSON object {#record_edit_object}

```json
{
  "Metadata": {
    "MergeStrategies": {
      "Description": "KEEP",
      "Keywords": "MERGE"
    },
    "Descriptive": {
      "Description": "Un nouveau dinosaure a été découvert en Argentine ! ...",
      "Keywords": {
        "Keyword": ["Argentine", "News", "Paléontologie", "RTL"]
      }
    },
    "Dynamic": {
      "OcariFRCollection": "RTL Actu (489965)",
      "VideoLink": "VideoLink",
      "OcariFRTopic": "Belgique",
      "Permalink": "XYZ"
    },
    "Technical": {
      "Md5": "8bdd0c5dc3ea6640e1553351edb45d87"
    }
  },
  "Reason": "new studies cleared up some parts of the paper",
  "EventType": "UPDATE",
  "Adoption": {
    "ParentRecordId": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
    "ForcedInheritance": false,
    "Candidate": true,
    "ProfileStrategy": "MERGE"
  },
  "PreviewRecordId": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
  "ChildOrderFields": {
    "Field": [
      {
        "DottedKey": "Descriptive.Title",
        "Direction": "asc"
      }
    ]
  }
}
```

#### Record update XML object {#record-create-object-xml}

```xml
<?xml version="1.0" encoding="UTF-8"?>
<UpdateRecord>
  <Title>My title</Title>
  <Metadata>
    <mhs:Sidecar xmlns:mhs="https://zeticon.mediahaven.com/metadata/19.2/mhs/"
                 xmlns:mh="https://zeticon.mediahaven.com/metadata/19.2/mh/" version="19.2">
      <mhs:Descriptive>
        <mh:Description strategy="KEEP">Un nouveau dinosaure a été découvert en Argentine ! ...</mh:Description>
        <mh:Keywords strategy="MERGE">
          <mh:Keyword>Argentine</mh:Keyword>
          <mh:Keyword>News</mh:Keyword>
          <mh:Keyword>Paléontologie</mh:Keyword>
          <mh:Keyword>RTL</mh:Keyword>
        </mh:Keywords>
      </mhs:Descriptive>
      <mhs:Dynamic>
        <OcariFRCollection>RTL Actu (489965)</OcariFRCollection>
        <VideoLink>http://vod-mp4.rtl.be/XXXXXXX.mp4</VideoLink>
        <OcariFRTopic>belgique</OcariFRTopic>
        <Permalink>XYZ</Permalink>
      </mhs:Dynamic>
      <mhs:Technical>
        <mh:Md5>8bdd0c5dc3ea6640e1553351edb45d87</mh:Md5>
        <mh:FileSize>1000</mh:FileSize>
      </mhs:Technical>
    </mhs:Sidecar>
  </Metadata>
  <Reason>new studies cleared up some parts of the paper</Reason>
  <EventType>UPDATE</EventType>
  <Adoption>
    <ParentRecordId>c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1</ParentRecordId>
    <ForcedInheritance>false</ForcedInheritance>
    <Candidate>true</Candidate>
    <ProfileStrategy>MERGE</ProfileStrategy>
  </Adoption>
  <PreviewRecordId>c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1</PreviewRecordId>
  <ChildOrderFields>
    <Field>
      <DottedKey>Descriptive.Title</DottedKey>
      <Direction>asc</Direction>
    </Field>
  </ChildOrderFields>
</UpdateRecord>
```

#### Response

- `200` Ok: [Record object](#record-object)
- `404` Not found
    - adoption.parentRecordId or PreviewRecordId can’t be found
- `400` Bad request: [error result](#error)
    - adoption.parentRecordId or previewRecordId contain an invalid record id
- `409` Conflict:
    - When violating the [record tree logic](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2291466251/Record+Tree)
    - When a concurrent update is happening (Code: `ECONCURRENT`). The client can retry his update.
    - When previewRecordId contains a record without valid browses. This means the BrowseStatus of the preview record is
      not equal to ‘Completed’.
- `412` Precondition Failed:
    - When
      a [metadata collision](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/5070487629/Version+Conflict+Detection)
      occurs

#### Authorization functions

- Any authenticated user can access this resource

### General editing limitations {#general_edit_limitations}

#### Update speed {#edit_field_limitations_speed}

While updating the metadata will be fast, it will not be instant. It is possible that if you request the object
immediately after editing, the old data will still be returned.

Using the LastModifiedDate field you can compare with a previous version and verify whether you have new or stale data.

## Browses {#browses}

### Generating browses for a record (retranscode) {#generate_browses}

Browses, or previews, of a record can be generated by performing a `POST` request with
a [BrowseRequest](#generate_browse_request) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/browses
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.  
This endpoint can also be used to regenerate all existing browses. This action is also known as retranscode or
retranscoding.

This is an asynchronous operation so there might be a delay between the request and the availability of the browses. The
progress can be followed by watching the [Internal.BrowseStatus](#browse_status) field of the record, it will have the
value `completed` if all browses were successfully generated.

#### BrowseRequest object example {#generate_browse_request}

| Property | Description | Required | Default |
| --- | --- | --- | --- |
| Encoding | Encoding options as used in the [Transformations object](#transformation_object) property `Encoding` | false | {} |
| ClusterGroups | Cluster groups where to store the browse | true | `[ "browse", "browse_backup" ]` |
| PronomId | Pronom ID of the [format](#formats) of the access representation to generate. Must point to a format that is allowed for access and has an extension defined. Only applicable to data objects when a custom encoding is provided | true (data objects when custom encoding is provided) |

```json
{
  "ClusterGroups": [
    "tape_vault"
  ],
  "Encoding": {
    "Width": 1920,
    "Height": 1080
  }
}
```

#### Response

- `202` Accepted: The browses are generating.
- `409` Conflict:
    - The browses are already generating.
    - The browses already exist and are stored on different cluster groups than the ones provided.
- `400` Bad request: [error result](#error)
    - The record has no file linked to it.
    - An empty array of cluster groups was provided.
    - Any of the provided cluster groups do not exist.
    - Any of the default cluster groups do not exist, when no cluster groups where provided.

#### Authorization functions

- Any authenticated user with write rights on the record can access this resource

## Reharvest {#reharvest}

Reharvest is the process of regenerating specific metadata fields that are typically generated automatically, most often by AI.
This is useful when metadata needs to be enriched after initial ingest.

Currently, the following features are used to reharvest metadata:
- `ExtractedMetadata`: Extracts burned-in metadata such as EXIF, XMP, etc., from the file and directly translates it into MediaHaven fields.
- `GenerativeMetadata`: Enables the creation of instructions for an AI model to generate various metadata fields.
- `Ocr`: Performs Optical Character Recognition (OCR) on objects, storing the results in the record metadata to enable text-based search within files.
- `Embeddings`: Supports semantic and similarity search by creating vector embeddings of the record’s content.

### Reharvesting metadata for a record {#reharvest}

Reharvesting metadata for a record can be initiated by performing a `POST` request with a [ReharvestRequest](#reharvest_request) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/reharvest
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

Notes:
- When using a `FragmentId`, reharvesting is only supported for main fragments. Pure fragments are not eligible for reharvesting.
- This is an asynchronous operation so there might be a delay between the request and the availability of the regenerated metadata.

#### Reharvest request object structure {#reharvest_request}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Features | List | A list of enum values indicating which (AI) features should be used to reharvest metadata for the record. Possible values are `Md5`, `ExtractedMetadata`, `GenerativeMetadata`, `Ocr`, `Embeddings`, `Insights`. | depends on the active plugins | no |
| ProfileId | String | The AI profile that should be used, specifying the configuration to apply during the reharvest process. | id of profile with tag `Default.Ai` | no |

```json
{
  "Features": [
    "GenerativeMetadata", 
    "Ocr", 
    "Embeddings",
    "Insights"
  ],
  "ProfileId": "214ac264-3d4a-48cb-b02d-b6641287655a"
}
```

#### Response

- `202` The reharvest is being processed.
- `400` The request is not valid.
- `403` User is not authorized.
- `404` The record or profile was not found.
- `409` Ingest of record is not completed yet.

#### Authorization functions

- Any authenticated user with write rights on the record can access this resource

## Conversion {#conversion}

Conversion enables the migration of existing (flat) data objects to richer data objects for improved consistency and
future compatibility.

### Convert to another main record type {#conversion_record}

Converting a (flat) data record from its current main record type to another main record type can be done by performing a `POST` request with
a [ConversionRequest](#conversion_request) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/conversion
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

> Notes: When using a `FragmentId`, conversion is only supported for main fragments. Pure fragments are not eligible for
> conversion.

#### Conversion request object structure {#conversion_request}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| TargetRecordType | String | The target main record type. It must have `RecordStructure` `Data` and must not be the same as the original | Dependent on the `DefaultRecordType` of the [Record scheme](#record_scheme_object) for the user’s organisation | yes |

```json
{
  "TargetRecordType": "Media"
}
```

#### Response

- `200` The converted [Record object](#record-object).
- `400` The request is not valid.
- `403` User is not authorized.
- `404` The record was not found.
- `409` The record cannot be converted in its current status.

#### Authorization functions

- Any authenticated user with write rights on the record can access this resource

## Search for records {#search-for-media-objects}

An api user can build up basic or advanced search queries by combining specific search terms and
free text and providing those into the request for a records resource. At first we will explain how to perform
some basic searching within MediaHaven then we will go into more advanced topics like searching in a specific
field, searching with wildcards and more.

### Basic searching {#basic-searching}

To search for records within MediaHaven you will use the `records`-endpoint.  
For example if you want to list the first 25 records with metadata containing ‘nature’,  
following `GET`-request can be used:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records?q=nature&startIndex=0&nrOfResults=25
```

| Query parameter | Type | Description | Default Value | Maximum |
| --- | --- | --- | --- | --- |
| q | String | Free text search string that supports [query syntax](#query-syntax). |  |  |
| sq | String | Semantic search string using plain text only (no query syntax). Requires additional module. |  |  |
| ftq | String | Full text search string using plain text only (no query syntax), also searches OCR-generated content. Requires additional module. |  |  |
| minimumScore | Float | The minimum score for semantic query results | Dependent on plugin | 1.0 |
| fields | List | The fields that should be exposed in the result. Dotted keys are supported and `Score`,`Context` (Can be combined with profiles) | \* (all) |  |
| fieldsToExclude | List | The fields that should be excluded from the result (Can be combined with profiles and fields) | Ai.\* |  |
| profiles | List | The profiles for which the fields should be returned (Can be combined with fields) |  |  |
| startIndex | Number | used for pagination, search results will be returned starting from this index | 0 |  |
| nrOfResults | Number | the number of results that will be returned | 25 | 100 |
| publicOnly | Boolean | `Deprecated property, might be removed in the future.` If true exclude from the output dynamic metadata fields which were marked as non public in the [Profiles](#profiles) linked with the record. | false |  |
| source | Enum(`SEARCH`, `DATABASE`) | The source from which the record should be fetched (only changeable if user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`) | SEARCH |  |
| applySigning | Boolean | Should the Keyframe, PathToPreview contain temporary uri’s | True |

> Note: `publicOnly` is deprecated, whether a field is returned depends on the active Classification profiles for a record. See [Classification profile field properties](#profile_field_classification_properties) for more info.
>
> `Score` will be returned as part of the `Context` object

You can also choose the format of the response by specifying the `Accept` header

Following formats are supported:

- Json: `application/json` [Example](#record-object) **(default)**
- MHS_HEAD: `application/xml` [Example](#sample_mhs_xml)
- Dublin core: `application/dc+xml` [Example](#sample_dc_xml)
- METS_MHS_HEAD: `application/mets+mhs+xml` [Example](#sample_mets_mhs_xml)

The webservice will respond with a [PagedResult](#page) object with the ‘Results’ being [Records](#record-object).

### Searching using POST {#searching-post}

To search for records using a `POST` request, the following endpoint can be used:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/search
```

The available properties are equivalent to [searching using GET](#basic-searching)

#### Example JSON body {#search-request-obj-json}

```json
{
  "Q": "Descriptive.Title:natuur",
  "NrOfResults": 25,
  "StartIndex": 0,
  "Sort": [
    "Administrative.LastModifiedDate,Desc"
  ]
}
```

#### Example XML body {#search-request-obj-xml}

```xml
<?xml version="1.0" encoding="UTF-8"?>
<SearchRecords>
    <Q>Descriptive.Title:natuur</Q>
    <NrOfResults>25</NrOfResults>
    <StartIndex>0</StartIndex>
    <Sort>
        <Field>Administrative.LastModifiedDate,Desc</Field>
    </Sort>
</SearchRecords>
```

### Total count {#count-searching}

To get only the total amount of items that match you search-query. A `HEAD`-request to the same endpoint for basic
searching can be used. The response will contain a header element with the name `Result-Count`.

You can also choose the format of the response by specifying the `Accept` header

### Query syntax {#query-syntax}

#### Free text search (global search) {#search_on_free_text}

Free text search can be used to search for records that includes one or more words within a free text field. The query
will be in following form:

```
q=value
```

All field definitions with property `GlobalSearch` = true can be considered as free text field.

The search behaves as follows: the search term is split into tokens based on word boundaries, excluding whitespace,
punctuation marks, symbols and other non-alphanumeric characters. Furthermore, stop words are removed and tokens are
stemmed.  
Results are always case-insensitive.

#### Field-specific search (advanced search) {#search_on_specific_fields}

Besides search with free text over all the searchable metadata fields it is also possible to search for specific fields
containing
a certain value. The query will be in following form:

```
q=fieldName:fieldValue
```

In order to search on a specific field, the property `AdvancedSearch` must be set to true for the related field
definition.
For example, if advanced search is enabled for field definition `Descriptive.Title`, you can search on this field using
the key or dotted key as field name:
`q=Descriptive.Title:book` or `q=Title:book`

The search behaviour depends on the field definition type:

- For `SimpleFields`, except `TextFields`, the search term is treated as a single keyword or token.
- For `TextFields`, the search term is split into tokens based on word boundaries, excluding whitespace, punctuation
  marks, symbols and other non-alphanumeric characters. Furthermore, stop words are removed and tokens are stemmed.

Results are always case-insensitive. If you want to do a case-sensitive search, you can use the original search variant.
This can be achieved by putting the suffix `_orig` after the field name. This search variant is available for
all `SimpleFields`, except `TextFields`.  
For example, if you want to do a case-sensitive search for the `Title` field, you can use following
query: `q=Descriptive.Title_orig:Book` or `q=Title_orig:Book`.
This variant is also used when requesting facets.

##### Examples

###### Search on title {#search_on_title}

`Title`

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Title:my_picture)"
```

###### Search on mediatype {#search_on_mediatype}

`Type`

###### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Type:image)"
```

###### Search on uploaded by {#search_on_uploader}

`UploadedBy`

You have to give the full name, not only the login.  
Add quotes around the name and place an + sign where you would set a space.

###### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(UploadedBy:"John+Smith")&startIndex=0&nrOfResults=5"
```

###### Search on author {#search_on_author}

`AuthorsAuthor`

###### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(AuthorsAuthor:"John+Smith")&startIndex=0&nrOfResults=5"
```

###### Search on keyword {#search_on_keyword}

`KeywordsKeyword`

###### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(KeywordsKeyword:nature)&startIndex=0&nrOfResults=5"

curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(KeywordsKeyword:"tropical+animals")&startIndex=0&nrOfResults=5"
```

###### Search on category {#search_on_category}

`CategoriesCategory`

###### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(CategoriesCategory:"Stock+pictures")&startIndex=0&nrOfResults=5"
```

###### Search on department {#search_on_department}

`DepartmentName`

###### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(DepartmentName:"public")&startIndex=0&nrOfResults=5"
```

#### Boolean search {#boolean_search}

Boolean search allows the user to produce more precise and targeted search results using boolean operators:

- Excluding a search term (NOT): `q=-searchterm`
- Combining search terms using an or mechanism, meaning that the results will contain either of the search terms (
  OR): `q=term1 term2`
- Combining search terms in such a way that both need to be available within the metadata (AND): `q=+term1 +term2`

#### Grouping search terms {#grouping_search_terms}

A query can be build up of multiple search terms, each search term that you want to include in the query needs to be
enclosed within parentheses `()`.
For example, the following query searches for results containing the term `cat` or `dog` and the
term `animal`: `q=+(cat dog) +animal`

Some examples will make this clearer:

##### Example 1: Searching for all videos made by sam with keyword “award” (Simple AND relation)

```
+(MediaObjectType:video) +(AuthorsAuthor:sam) +(KeywordsKeyword:award)

https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Type:video)%20%2B(AuthorsAuthor:sam)%20%2B(KeywordsKeyword:award)
```

##### Example 2: Searching for all video or audio files (simple OR relation)

```
+(Type:video Type:audio)

https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Type:video Type:audio)
```

##### Example 2: Searching for several specific objects by id (simple OR relation)

```
+(FragmentId:825cb5efe6b54029a6bd11444be1ed94bc3b2b753dcb6a64ea6baa6711264a8472ebea844873f228c3b FragmentId:a7c2164a983a4050ad653924e8b7f39d70fb6b2923c84f38b7aa543d6ad32cf85e971b5f506f3363b26c9d8120634377)

https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(FragmentId:825cb5efe6b54029a6bd11444be1ed94bc3b2b753dcb6a64ea6baa6711264a8472ebea844873f228c3b FragmentId:a7c2164a983a4050ad653924e8b7f39d70fb6b2923c84f38b7aa543d6ad32cf85e971b5f506f3363b26c9d8120634377)
```

##### Example 3: Searching for a collection, the name of the collection starts with Wine or Beer (mixed AND/OR relation)

```
+(Type:Collection) +(Title:Wine* Title:Beer*)

https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Type:Collection)%20%2B(Title:Wine* Title:Beer*)
```

##### Example 4: Search for all images that do not have “nsfw” as keyword (mixed AND/NOT relation)

```
+(Type:Image) -(KeywordsKeyword:nsfw)

https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Type:Image)%20-(KeywordsKeyword:nsfw)
```

#### Phrase search {#phrase_search}

A phrase is a group of words surrounded by double quotes. Phrase search allows you to find exact phrases or sequences of
words within a search query. Example query: `q="red panda"`

#### Wildcard search {#wildcard_search}

Wildcards take the place of one or more characters in a search term. A question mark `?` is used for single character
searching, an asterisk `*` is used for multiple character searching.
For example, when searching for the text: `Reception` you can use following wildcards:

```
q=Re?eption
q=Recep*
q=Rec*ion
```

Wildcard characters can not be applied to search phrases or search terms containing multiple tokens.

#### Semantic search {#semantic_search}

This type of search is intended to improve the quality of search results by interpreting natural language more accurately and in context.
It uses AI and machine learning to improve the search results.

```
sq=Show pictures of cats
```

Additional modules are required to be able to use semantic search
.

#### Date search {#search_on_date}

DateFields should be formatted in the ISO8601 date format: `yyyy-mm-ddThh:mm:ssZ` or `yyyy-mm-ddThh:mm:ss.SSSSSSZ`.  
Range searches are supported via the following syntax:

- `[ TO ]` inclusive range
- `{ TO }` exclusive range
- `[ TO }`, `{ TO ]` mix of inclusive and exclusive range

| Description | Query | Example |
| --- | --- | --- |
| specific time | “2016-01-08T12:59:04Z” | LastModifiedDate:”2016-01-08T12:59:04Z” |
| specific time with 6 digits after the decimal | “2016-01-08T12:59:04.123456Z” | LastModifiedDate:”2016-01-08T12:59:04.123456Z” |
| specific day (08 jan 2016) | [“2016-01-08T00:00:00Z” TO “2016-01-09T00:00:00Z”} | LastModifiedDate:[“2016-01-08T00:00:00Z” TO “2016-01-09T00:00:00Z”} |
| from 08/01 up to 10/01 (exclusive) | [“2016-01-08T00:00:00Z” TO “2016-01-10T00:00:00Z”} | LastModifiedDate:[“2016-01-08T00:00:00Z” TO “2016-01-10T00:00:00Z”} |
| from 08/01 to the end of time | [“2016-01-08T00:00:00Z” TO \*] | LastModifiedDate:[“2016-01-08T00:00:00Z” TO \*] |
| from the beginning of time up to 10/01 (exclusive) | [\* TO “2016-01-10T00:00:00Z”} | LastModifiedDate:[\* TO “2016-01-10T00:00:00Z”} |

##### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(LastModifiedDate:%5B%222016-01-08%22+TO+%222016-01-09T23:59:59Z%22%5D)"
```

#### Spatial search {#search_on_location}

The engine supports spatial search for `GeoCoordinateField`s and makes it possible to filter by an arbitrary
rectangle.  
This can be achieved using the range query syntax by supplying the lower-left corner as the start of the range and the
upper-right corner as the end of the range.  
For example: `q=Descriptive.Position.Location:[45.01,23.85 TO 46.23,-93.16]`

##### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Descriptive.Position.Location:%5B45.01,23.85 TO 46.23,-93.16%5D)"
```

#### Escaping Special Characters

MediaHaven supports escaping special characters that are part of the query syntax. The current list special characters
are

```
+ - && || ! ( ) { } [ ] ^ " ~ * ? : \ /
```

To escape these character use the \ before the character. For example to search for (1+1):2 use the query:

```
\(1\+1\)\:2
```

Also note that, since the search query is send as part of a query string, certain characters need to be URL encoded.
Though depending on the technology you use to sent the request, this might be done automatically.

| Character | Url encoding |
| --- | --- |
| + | %2B |
| Space | %20 or + |

#### Searching all records in collection {#get_collection}

Getting all records in a collection.

Note the asterisk \* at the end is important.

##### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(CollectionsCollection:db63a8d272884bb0943e9c98e98707362d6fdde1fb234e4a9fdd71d4b26c292d*)&startIndex=0&nrOfResults=5"
```

Example search for collection

This example shows a fictional example of how collections can be retrieved,  
the parameters in this example should be replaced to match your specific use case:

- First we search for objects called: “press conference” (exact match)
- We receive results, and one of the results is of “type”:”Collection”, and with “mediaObjectId”:”
  a7c2164a983a4050ad653924e8b7f39d70fb6b2923c84f38b7aa543d6ad32cf8”
- We can get the objects in that Collection with the following query:

```http
CollectionsCollection:a7c2164a983a4050ad653924e8b7f39d70fb6b2923c84f38b7aa543d6ad32cf8*
```

- Those objects can be again images, videos, collections, …

##### cURL

Search for objects called: “press conference” (exact match)

```
?q=%2B(Title:%press%20conference%22)
```

```bash
C:\Users\Fred>curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(Title:%press%20confe
rence%22)"
HTTP/1.1 200 OK
Server: Apache-Coyote/1.1
Content-Type: application/json
Transfer-Encoding: chunked
Date: Mon, 27 Jan 2014 10:07:01 GMT

{
    "NrOfResults": 1,
    "TotalNrOfResults": 1,
    "StartIndex": 0,
    "Results": [
        {
            "Technical": {
                "OriginalExtension": "zip",
                "FileSize": 0,
                "PronomId": null,
                "Md5": null,
                "MimeType": null,
                "Width": null,
                "Height": null,
                "ImageSize": null,
                "ImageOrientation": null,
                "ImageQuality": null,
                "VideoTechnical": null,
                "AudioTechnical": null,
                "VideoFormat": null,
                "DurationTimeCode": null,
                "StartTimeCode": null,
                "EndTimeCode": null,
                "DurationFrames": null,
                "StartFrames": null,
                "EndFrames": null,
                "VideoCodec": null,
                "VideoFps": null,
                "VideoBitRate": null,
                "BitRate": null
            },
            "Descriptive": {
                "Title": "press conference",
                "OriginalFilename": "wc.zip",
                "UploadedBy": "Bulk Upload",
                "KeyframeStart": 0,
                "RightsOwner": "© DEVELOP",
                "CreationDate": "2020-01-14T20:20:21.000000Z",
                "Description": null,
                "Rights": null,
                "Keywords": {
                    "Keyword": []
                },
                "Categories": {
                    "Category": []
                },
                "Publisher": null,
                "Authors": {},
                "Location": null,
                "Address": {},
                "NonPreferredTerm": null,
                "Publications": null
            },
            "Structural": {
                "Versioning": {
                    "Status": "Untracked",
                    "Version": 1
                },
                "Sets": {
                    "Set": []
                },
                "Collections": {
                    "Collection": []
                },
                "Newspapers": {
                    "Newspaper": []
                },
                "Relations": {},
                "Fragments": {},
                "FragmentStartFrames": null,
                "FragmentEndFrames": null,
                "FragmentDurationTimeCode": null,
                "FragmentStartTimeCode": null,
                "FragmentEndTimeCode": null,
                "FragmentDurationFrames": null
            },
            "Internal": {
                "MediaObjectId": "0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de",
                "FragmentId": "0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de654832ce77664161ab4d3f14b28247da",
                "OriginalStatus": "in_progress",
                "BrowseStatus": "in_progress",
                "ArchiveStatus": "in_progress",
                "UploadedById": "ff100a7a-efd0-44e3-8816-0905572421da",
                "OrganisationId": "100",
                "IsInIngestSpace": false,
                "DepartmentId": "dd100b7a-efd0-44e3-8816-0905572421da",
                "IsFragment": false,
                "HasKeyframes": false,
                "ContainsGeoData": false,
                "PathToKeyframe": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277/browse.jpg",
                "PathToKeyframeThumb": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277/browse-thumb.jpg",
                "Browses": {
                    "Browse": [
                        {
                            "BaseUrl": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277",
                            "PathToKeyframe": "browse.jpg",
                            "PathToKeyframeThumb": "browse-thumb.jpg",
                            "HasKeyframes": false
                        }
                    ]
                },
                "IngestSpaceId": null,
                "PathToVideo": null
            },
            "Administrative": {
                "OrganisationName": "develop",
                "LastModifiedDate": "2020-01-14T19:20:21.000000Z",
                "ExternalId": "develop_wc_zip",
                "ArchiveDate": "2020-01-14T20:20:21.000000Z",
                "Type": "collection",
                "DepartmentName": "develop",
                "IsSynchronized": false,
                "OrganisationLongName": "develop",
                "IsOriginal": true,
                "IsPreservation": false,
                "IsAccess": false,
                "Workflow": null,
                "IngestTape": null
            },
            "RightsManagement": {
                "Permissions": {
                    "Read": [
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "de100b7a-efd0-44e3-8816-0905572421da",
                        "df100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "da100b7a-efd0-44e3-8816-0905572421da"
                    ],
                    "Write": [
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "da100b7a-efd0-44e3-8816-0905572421da"
                    ],
                    "Export": [
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "da100b7a-efd0-44e3-8816-0905572421da"
                    ]
                },
                "ExpiryDate": null,
                "ExpiryStatus": null
            },
            "Context": {
                "IsEditable": true,
                "IsDeletable": true,
                "IsPublic": true,
                "IsExportable": true
            }
        }
    ]
}
```

We received results, and one of the results is of `"type":"Collection"`, and
with `"mediaObjectId":"0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de"`
Get all objects in the collection “0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de”

```
?q=%2B(CollectionsCollection:0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de*)
```

```bash
C:\Users\Fred>curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(CollectionsCollection:a7c2164a983a4050ad653924e8b7
f39d70fb6b2923c84f38b7aa543d6ad32cf84*)"
HTTP/1.1 200 OK
Server: Apache-Coyote/1.1
Content-Type: application/json
Transfer-Encoding: chunked
Date: Mon, 27 Jan 2014 09:50:59 GMT

{
    "NrOfResults": 1,
    "TotalNrOfResults": 1,
    "StartIndex": 0,
    "Results": [
        {
            "Technical": {
                "PronomId": "fmt/12",
                "OriginalExtension": "png",
                "FileSize": 8233248,
                "Md5": "354bd34a91467fdfb092e3e51720308d",
                "MimeType": "image/png",
                "Width": 4896,
                "Height": 3264,
                "ImageSize": "4896x3264",
                "ImageQuality": "high",
                "ImageOrientation": "landscape",
                "VideoTechnical": null,
                "AudioTechnical": null,
                "VideoFormat": null,
                "DurationTimeCode": null,
                "StartTimeCode": null,
                "EndTimeCode": null,
                "DurationFrames": null,
                "StartFrames": null,
                "EndFrames": null,
                "VideoCodec": null,
                "VideoFps": null,
                "VideoBitRate": null,
                "BitRate": null
            },
            "Descriptive": {
                "Title": "DigiHaven-by-Zeticon.png",
                "OriginalFilename": "DigiHaven-by-Zeticon.png",
                "UploadedBy": "zeticon@develop",
                "KeyframeStart": 0,
                "RightsOwner": "© DEVELOP",
                "CreationDate": "2019-08-13T17:58:18.000000Z",
                "Description": null,
                "Rights": null,
                "Keywords": {
                    "Keyword": []
                },
                "Categories": {
                    "Category": []
                },
                "Publisher": null,
                "Authors": {},
                "Location": null,
                "Address": {},
                "NonPreferredTerm": null,
                "Publications": null
            },
            "Structural": {
                "Collections": {
                    "Collection": [
                        "0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de_0000000000"
                    ]
                },
                "FragmentStartFrames": 0,
                "FragmentEndFrames": 0,
                "Versioning": {
                    "Status": "Untracked",
                    "Version": 1
                },
                "Sets": {
                    "Set": []
                },
                "Newspapers": {
                    "Newspaper": []
                },
                "Relations": {},
                "Fragments": {},
                "FragmentDurationTimeCode": null,
                "FragmentStartTimeCode": null,
                "FragmentEndTimeCode": null,
                "FragmentDurationFrames": null
            },
            "Internal": {
                "MediaObjectId": "4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277",
                "FragmentId": "4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c27770201499b9bc49c0a1e314ad2487a710",
                "OriginalStatus": "completed",
                "BrowseStatus": "completed",
                "ArchiveStatus": "on_disk",
                "UploadedById": "ff100a7a-efd0-44e3-8816-0905572421da",
                "OrganisationId": "100",
                "IsInIngestSpace": false,
                "DepartmentId": "dd100b7a-efd0-44e3-8816-0905572421da",
                "IsFragment": false,
                "HasKeyframes": false,
                "ContainsGeoData": false,
                "PathToKeyframe": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277/browse.jpg",
                "PathToKeyframeThumb": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277/browse-thumb.jpg",
                "Browses": {
                    "Browse": [
                        {
                            "BaseUrl": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277",
                            "PathToKeyframe": "browse.jpg",
                            "PathToKeyframeThumb": "browse-thumb.jpg",
                            "HasKeyframes": false,
                            "Container": "jpg",
                            "Label": "jpg",
                            "FileSize": 159061,
                            "Width": 2000,
                            "Height": 1333
                        }
                    ]
                },
                "IngestSpaceId": null,
                "PathToVideo": null
            },
            "Administrative": {
                "OrganisationName": "develop",
                "LastModifiedDate": "2020-01-14T19:20:36.000000Z",
                "ExternalId": "develop_DigiHaven-by-Zeticon_png",
                "ArchiveDate": "2020-01-14T20:20:21.000000Z",
                "Type": "image",
                "DepartmentName": "develop",
                "IsSynchronized": false,
                "OrganisationLongName": "develop",
                "IsOriginal": true,
                "IsPreservation": false,
                "IsAccess": false,
                "Workflow": null,
                "IngestTape": null
            },
            "RightsManagement": {
                "Permissions": {
                    "Read": [
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "da100b7a-efd0-44e3-8816-0905572421da"
                    ],
                    "Write": [
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "da100b7a-efd0-44e3-8816-0905572421da"
                    ],
                    "Export": [
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "da100b7a-efd0-44e3-8816-0905572421da"
                    ]
                },
                "ExpiryDate": null,
                "ExpiryStatus": null
            },
            "Context": {
                "IsEditable": true,
                "IsDeletable": true,
                "IsPublic": true,
                "IsExportable": true
            }
        }
    ]
}
```

#### Searching in ingestspaces {#get_ingestspace}

Searching in ingestspaces is turned off by default. To enable this, the `IsInIngestSpace` field is used.
Possible values are:

- `0` : Don’t search in ingestspaces `(default)`
- `1` : Only search in ingestspaces
- `*` : Search everywhere

To limit the search to a specific ingestspace, the `IngestSpaceId` field can be used, followed by the IngestSpaceId.
Note that the id of the ingestspace must be put between “double quotes” (or use the url_encoded form: %22) to ensure
proper results. [This section](#current_user) explains how to request the ingestspace ids accessible to the current
user.

When objects leave their ingestspace, this `IngestSpaceId` field will remain set. This can be used to track the origin
of the objects.

##### cURL

Search for all objects that are currently in an ingestspace with id: “e94e4271-4881-405d-9a4e-4335cef8ef66”

```
?q=%2B(IsInIngestSpace:1)+%2B(IngestSpaceId:%22e94e4271-4881-405d-9a4e-4335cef8ef66%22)
```

```bash
C:\Users\Fred>curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(IsInIngestSpace:1)+%2B(IngestSpaceId:%22e94e4271-4881-405d-9a4e-4335cef8ef66%22)"
HTTP/1.1 200 OK
Date: Wed, 22 Oct 2014 14:09:35 GMT
Server: Apache/2.2.22 (Debian)
Content-Length: 1109
Content-Type: application/json

{
   "NrOfResults" : 25
   "TotalNrOfResults": 34,
   "StartIndex": 0,
   "Results": [
        {
            "Technical": {
                "PronomId": "fmt/43",
                "OriginalExtension": "jpg",
                "FileSize": 57592,
                "Md5": "64280691e1a0a9a3a7c0244fcb242309",
                "MimeType": "image/jpeg",
                "Width": 726,
                "Height": 727,
                "ImageSize": "726x727",
                "ImageQuality": "low",
                "ImageOrientation": "square",
                "VideoTechnical": null,
                "AudioTechnical": null,
                "VideoFormat": null,
                "DurationTimeCode": null,
                "StartTimeCode": null,
                "EndTimeCode": null,
                "DurationFrames": null,
                "StartFrames": null,
                "EndFrames": null,
                "VideoCodec": null,
                "VideoFps": null,
                "VideoBitRate": null,
                "BitRate": null
            },
            "Descriptive": {
                "Title": "ugzclx5r1a741.jpg",
                "OriginalFilename": "ugzclx5r1a741.jpg",
                "UploadedBy": "Zeticon Support",
                "KeyframeStart": 0,
                "RightsOwner": "© DEVELOP",
                "CreationDate": "2020-01-15T14:46:09.000000Z",
                "Description": null,
                "Rights": null,
                "Keywords": {
                    "Keyword": []
                },
                "Categories": {
                    "Category": []
                },
                "Publisher": null,
                "Authors": {},
                "Location": null,
                "Address": {},
                "NonPreferredTerm": null,
                "Publications": null
            },
            "Structural": {
                "FragmentStartFrames": 0,
                "FragmentEndFrames": 0,
                "Versioning": {
                    "Status": "Untracked",
                    "Version": 1
                },
                "Sets": {
                    "Set": []
                },
                "Collections": {
                    "Collection": []
                },
                "Newspapers": {
                    "Newspaper": []
                },
                "Relations": {},
                "Fragments": {},
                "FragmentDurationTimeCode": null,
                "FragmentStartTimeCode": null,
                "FragmentEndTimeCode": null,
                "FragmentDurationFrames": null
            },
            "Internal": {
                "MediaObjectId": "5147a9ba468f405aab9752bd2bbb0718f2a910707d4647bebacbd4430ed5eee6",
                "FragmentId": "5147a9ba468f405aab9752bd2bbb0718f2a910707d4647bebacbd4430ed5eee61987f8937dfd48a9b078dc3c23105090",
                "OriginalStatus": "completed",
                "BrowseStatus": "completed",
                "ArchiveStatus": "on_disk",
                "UploadedById": "ff100b7a-efd0-44e3-8816-0905572421da",
                "OrganisationId": "100",
                "IngestSpaceId": "e94e4271-4881-405d-9a4e-4335cef8ef66",
                "IsInIngestSpace": true,
                "IsFragment": false,
                "HasKeyframes": false,
                "ContainsGeoData": false,
                "PathToKeyframe": "https://develop.mediahaven.com/DEVELOP/5147a9ba468f405aab9752bd2bbb0718f2a910707d4647bebacbd4430ed5eee6/browse.jpg",
                "PathToKeyframeThumb": "https://develop.mediahaven.com/DEVELOP/5147a9ba468f405aab9752bd2bbb0718f2a910707d4647bebacbd4430ed5eee6/browse-thumb.jpg",
                "Browses": {
                    "Browse": [
                        {
                            "BaseUrl": "https://develop.mediahaven.com/DEVELOP/5147a9ba468f405aab9752bd2bbb0718f2a910707d4647bebacbd4430ed5eee6",
                            "PathToKeyframe": "browse.jpg",
                            "PathToKeyframeThumb": "browse-thumb.jpg",
                            "HasKeyframes": false,
                            "Container": "jpg",
                            "Label": "jpg",
                            "FileSize": 60387,
                            "Width": 726,
                            "Height": 727
                        }
                    ]
                },
                "DepartmentId": null,
                "PathToVideo": null
            },
            "Administrative": {
                "OrganisationName": "develop",
                "LastModifiedDate": "2020-01-15T13:46:11.000000Z",
                "ArchiveDate": "2020-01-15T14:46:09.000000Z",
                "Type": "image",
                "IsSynchronized": false,
                "OrganisationLongName": "develop",
                "IsOriginal": true,
                "IsPreservation": false,
                "IsAccess": false,
                "ExternalId": null,
                "DepartmentName": null,
                "Workflow": null,
                "IngestTape": null
            },
            "RightsManagement": {
                "Permissions": {
                    "Read": [
                        "df100b7a-efd0-44e3-8816-0905572421da",
                        "de100b7a-efd0-44e3-8816-0905572421da",
                        "e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "da100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6"
                    ],
                    "Write": [
                        "e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "da100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6"
                    ],
                    "Export": [
                        "e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
                        "dd100b7a-efd0-44e3-8816-0905572421da",
                        "da100b7a-efd0-44e3-8816-0905572421da",
                        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6"
                    ]
                },
                "ExpiryDate": null,
                "ExpiryStatus": null
            },
            "Context": {
                "IsEditable": true,
                "IsDeletable": true,
                "IsPublic": true,
                "IsExportable": true
            }
        },
        ...
    ]
}
```

### Pagination of results {#paging_results}

The other 2 arguments are used to limit the number of results (pagination):

- startIndex = used for pagination of searchresults, searchresults will be returned starting from this index. E.g.
  index=0 starts from the first result, index=1 from the second result.
- nrOfResults = the number of results that will be returned

So for using pagination, a first query will be: startIndex=0, nrOfResults=10, followed by startIndex=10, nrOfResults=10
for 2nd page and so on. By using the totalNrOfResults in the SearchResult
you can determine how many pages will be needed to show all the results.

##### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?q=%2B(KeywordsKeyword:nature)&startIndex=10&nrOfResults=10"
```

### Field selection {#field_selection}

To return only specific fields you can provide a list of dotted keys of the fields you want to see.

##### cURL

```bash
curl -D- -X GET -H "Authorization: Bearer ZnJlZDpmcmVk" "https://archief.viaa.be/mediahaven-rest-api/v2/records/?fields=Descriptive.Description&startIndex=10&nrOfResults=10"
```

Take note that we always return Internal.MediaObjectId,Internal.RecordId,Internal.RecordStatus, Permissions.\*, Internal.Profiles,Administrative.RecordType

### Sorting search results {#sorting_results}

To sort the results using one of the [available fields](#search_on_fields), use the `sort` keyword.

The `sort` keyword should contain a FlatKey, optionally followed by a comma and the direction.
The direction can be `asc`, `up`, `desc` or `down`. Capitalization doesn’t matter.
If no direction is provided, `asc` will be used by default.
The `sort` query parameter can be used up to 5 times in order to define sorting on multiple fields. The first `sort`
param defines the primary sort field, the second the secondary, etc.

So, for example, the following sorts the results on Title reverse-alphabetically (Z to A). When two or more results have
an identical title, the result with the earlier LastModifiedDate will appear first.

```
?q=...&sort=Descriptive.Title,down&sort=Administrative.LastModifiedDate,up
```

The fields that are always available are listed [here](#search_on_fields), but others might be available depending on
the installation.

### Recycled records {#recycled-records}

To search for logically deleted records within MediaHaven, use the `records/recycled`-endpoint.
This endpoint functions exactly like the regular search endpoints — both [GET on records](#basic-searching) AND [POST on records](#searching-post) — including the same parameters, headers, and response codes.
It returns only logically deleted records that can be restored. The following records are not included in the response:

- Flat data or representation records that have
  been [destructed](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/4137254971/Destruction)
- Rejected records
  <https://archief.viaa.be/mediahaven-rest-api/v2/records/recycled?q=nature&startIndex=0&nrOfResults=25>

### Getting a specific record {#get_record}

It is possible to retrieve all information about a specific object by its `Id`.

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/records/:id
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

| Query parameter | Type | Description | Default Value |
| --- | --- | --- | --- |
| publicOnly | Boolean | `Deprecated property, might be removed in the future.` If true, exclude from the output dynamic metadata fields which were marked as non public in the [Profiles](#profiles) linked with the record. | false |
| fields | array | Select only specific fields. Supports `Exif`, dotted keys and `Context`. If the record has record structure Data, the information for Exif is obtained from the original representation. (Can be combined with profiles) | \* |
| fieldsToExclude | array | The fields that should be excluded from the result (Can be combined with profiles and fields) | Ai.\* |
| profiles | array | The profiles for which the fields should be returned (Can be combined with fields) |  |
| includeDeleted | Boolean | If true, also return the record if it has been logically deleted | false |
| source | Enum(`SEARCH`, `DATABASE`) | The source from which the record should be fetched (only changeable if user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`) | SEARCH |

> Note: `publicOnly` is deprecated, whether a field is returned depends on the active Classification profiles for a
> record. See [Classification profile field properties](#profile_field_classification_properties) for more info.

You can also choose the format of the response by specifying the `Accept` header

Following formats are supported:

- Json: `application/json` [Example](#record-object) **(default)**
- MHS_HEAD: `application/xml` [Example](#sample_mhs_xml)
- Dublin core: `application/dc+xml` [Example](#sample_dc_xml)
- METS_MHS_HEAD: `application/mets+mhs+xml` [Example](#sample_mets_mhs_xml)

#### Response

- `200` Ok. A Record object
- `404` The record or one the profiles was not found.
- `406` The requested media type is not supported.

#### Field select

When using `Exif` for field select we return all data including the Exif data. You can use the dotted key variant `Technical.Exif` to only select the Exif information.

## Faceted search {#facet_search}

Faceted search categorizes and groups record data by specific fields, with each facet representing a field and showing the count of results for each distinct value.
The response for each requested facet includes a list of values that match the provided query and filter criteria.

Facets can be obtained via `GET` or `POST`. However, it is recommended to use the [Record facets POST](#facet_post_preferred) method, which provides the most user-friendly approach.

### Searching using GET (Legacy) {#facet_get}

Using `GET` you have 2 options, request all facets defined in a profile, or request a specific facet

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/facets
```

> Note: This endpoint is deprecated. Use [Record facets POST](#facet_post_preferred) for a more intuitive and efficient way to request facets for records.

| Query parameter | Description | Default Value |
| --- | --- | --- |
| q | Restrict to facets based on records matching the query, can be empty |  |
| sq | Restrict to facets based on records matching the semantic query, can be empty (requires additional module) |  |
| locale | Use this locale for translation of the labels and restrict facets if desired (see query parameter localeOnly) | user locale |
| localeOnly | Restrict to facets having the requested locale language or having no language property. If locale is not set, the user locale is used | false |
| includeActiveValues | `Deprecated property, might be removed in the future.` Include values which are present as pure MUST terms in the query (e.g. +Descriptive.Keywords.Keyword:Cork) | false |
| includeMissingValue | `Deprecated property, might be removed in the future.` Include the missing value (e.g. No Keywords) | true |
| includeEmptyFacets | `Deprecated property, might be removed in the future.` Return facets with no results | false |
| profileId | Id of the facet profile which contains the configuration for the requested facets | id of facet profile with tag `Default.Facet` |

> Note: With the introduction of the parameter `profileId`, the parameters `includeMissingValue` and `includeEmptyFacets` are no longer relevant,
> since these values are determined per facet within the facet profile, namely by the properties `IncludeMissingValue` and `HideEmpty`

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/facets/:dottedKey
```

| Query parameter | Description | Default Value |
| --- | --- | --- |
| q | Restrict to facets based on records matching the query, can be empty |  |
| sq | Restrict to facets based on records matching the semantic query, can be empty (requires additional module) |  |
| valueFilter | Restrict values to those that start with the provided value. |  |
| valueFilterOption.contains | Match also on results which contain the provided `valueFilter` at any point. e.g. Zea in New-Zealand. | false |
| valueFilterOption.containsIgnoreCase | Match on the provided `valueFilter` in a case-insensitive manner if `valueFilterOption.contains` is true. | false |
| nrOfResults | The number of results that will be returned |  |
| startIndex | Used for pagination, facet results will be returned starting from this index |  |
| locale | Use this locale for translation of the labels and restrict facets if desired (see query parameter localeOnly) | user locale |
| localeOnly | Restrict to facets having the requested locale language or having no language property. If locale is not set, the user locale is used | false |
| includeActiveValues | Include values which are present as pure MUST terms in the query (e.g. +Descriptive.Keywords.Keyword:Cork) | false (if facet not present in profile) |
| includeMissingValue | Include the missing value (e.g. No Keywords) | true (if facet not present in profile) |
| includeEmptyFacets | Return facets with no results | false (if facet not present in profile) |
| profileId | Id of the facet profile which contains the configuration for the requested facet | id of facet profile with tag `Default.Facet` |
| includeProfileFacetsOnly | Restrict to facets configured in the given facet profile | false |

> Note: `valueFilter` and `valueFilterOption` is not applicable for fields of type DateField, LongField, FramesField and BooleanField.
> Note: If `includeProfileFacetsOnly` is false and the facet profile does not contain the requested facet, a facet configuration with default values is used. The default values are the same as used in [facet profile properties](#profile_field_facet_properties)
> Note: If no value is given for `includeActiveValues`, `includeMissingValue` or `includeEmptyFacets`, their values are determined by the corresponding facet profile field, if present, based on its properties: `includeActiveValues`, `includeMissingValue` and `hideEmpty`

### Searching using POST (Legacy) {#facet_post_legacy}

Using `POST`, more advanced options are available (filtering, paginating, selection type, queries of arbitrary length). All facets defined in a profile or one specific facet can be requested:

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/facets

POST https://archief.viaa.be/mediahaven-rest-api/v2/facets/:dottedKey
```

With body [Facet request](#facet_request_object_legacy).

> Note: This endpoint is deprecated. Use [Record facets POST](#facet_post_preferred) for a more intuitive and efficient way to request facets for records.

#### Response

- `200` JSON Array of [Facet result](#facet_result_object_legacy)
- `400` The request contains invalid properties
- `403` User is not authorized
- `404` The profile id or facet could not be found

### Searching using POST (Preferred) {#facet_post_preferred}

To search for facets, send a `POST` request to:

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/records/facets
```

With body [Facet request](#facet_request_object_preferred).

#### Response

- `200` JSON Array of [Facet result](#facet_result_object)
- `400` The request contains invalid properties
- `403` User is not authorized
- `404` The profile id could not be found

### Obtaining facet configuration (Legacy) {#facet_config_get}

Returns the list of configured facets with their default settings applied during querying.

#### Using GET

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/facets/config
```

| Query parameter | Description | Default Value |
| --- | --- | --- |
| profileId | Id of the facet profile which contains the configuration for the requested facets | id of facet profile with tag `Default.Facet` |

> Note: This endpoint is deprecated. Instead, the [Profiles](#profiles_get_single) endpoint can be used to obtain the facet configuration for a specific facet profile.

#### Response

- `200` List of [Facet Definition options](#facet_definition_object)
- `400` The profile id is not valid
- `403` User is not authorized or has no access to the profile
- `404` The profile id could not be found

### Facet result object (legacy) {#facet_result_object_legacy}

| Property | Type | Description | Default value |
| --- | --- | --- | --- |
| DottedKey | String | The fully qualified key of the field on which the facet is based. |  |
| Label | String | The translation of the field based on the requested locale or the locale of the user. |  |
| Count | Number | The total number of distinct of facet values for all records matching the query and selected facet values, typically much larger than the actual included facet values (limited to typically 10). |  |
| Values | Values[] | A list of facet values. |  |
| Values.MustQuery | String | `Deprecated, might be removed in the future.` The query when including the facet value and already selected facet values from the facet request. |  |
| Values.MustNotQuery | String | `Deprecated, might be removed in the future.` The query when excluding the facet value and including the already selected facet values from the facet request. |  |
| Values.Value | String | The value of the facet. |  |
| Values.Label | String | The translation of the facet value, if no translation exists it equals the facet value. |  |
| Values.Count | Number | The number of records having this value. |  |
| Values.Missing | Boolean | Indicates if the facet value corresponds with the missing / empty facet value. |  |
| Values.Start | Date | The start date of the value (only applicable for date facets). |  |
| Values.End | Date | The end date of the value. Not included in the interval (only applicable for date facets). |  |
| Values.Gap | Enum | The size of the gap between start and end. Possible values are YEAR,MONTH or DAY. (only applicable for date facets). |

```json
{
  "DottedKey": "Descriptive.Keywords.Keyword",
  "Label": "Trefwoord",
  "Count": 987,
  "Values": [
    {
      "MustQuery": "+Global:Ireland +Descriptive.Keywords.Keyword:Cork",
      "MustNotQuery": "+Global:Ireland -Descriptive.Keywords.Keyword:Cork",
      "Value": "Cork",
      "Label": "Cork",
      "Count": 423,
      "Missing": false
    },
    {
      "MustQuery": "+Global:Ireland +Descriptive.Keywords.Keyword:Dublin",
      "MustNotQuery": "+Global:Ireland -Descriptive.Keywords.Keyword:Dublin",
      "Value": "Dublin",
      "Label": "Dublin",
      "Count": 58,
      "Missing": false
    },
    {
      "MustQuery": "+Global:Ireland -Descriptive.Keywords.Keyword:*",
      "MustNotQuery": "+Global:Ireland +Descriptive.Keywords.Keyword:*",
      "Value": "No keyword",
      "Label": "Geen trefwoord",
      "Count": 9871,
      "Missing": true
    }
  ]
}
```

### Facet request object (Legacy) {#facet_request_object_legacy}

| Property | Type | Description | Default value | Limits |
| --- | --- | --- | --- | --- |
| Q | String | Restrict to facets based on records matching the query, can be empty |  |  |
| Sq | String | Restrict to facets based on records matching the semantic query, can be empty (requires additional module) |  |  |
| Locale | String | Use this locale for translation of the labels and restrict facets if desired (see property `LocaleOnly`) | user locale | as configured |
| IncludeFilteredOnly | Boolean | Include only the facets defined in the Facets property | true if requesting a specific facet, otherwise false |  |
| LocaleOnly | Boolean | Restrict to facets having the requested locale language or having no language property. If Locale is not set, the user locale is used | false |  |
| ProfileId | String | Id of the facet profile which contains the configuration for the requested facets | id of facet profile with tag `Default.Facet` |  |
| IncludeProfileFacetsOnly | Boolean | Restrict to facets configured in the given facet profile | true |  |
| IncludeActiveValues | Boolean | Include values which are present as pure MUST terms in the query (e.g. +Descriptive.Keywords.Keyword:Cork) | false |  |
| IncludeMissingValue | Boolean | Include the missing value (e.g. No Keywords) | true |  |
| IncludeEmptyFacets | Boolean | Return facets with no results | false |  |
| Facets.NrOfResults | Number | The number of results that will be returned |  | [1,100] |
| Facets.DottedKey | String | The key of the facet |  |  |
| Facets.StartIndex | Number | Used for pagination, facet results will be returned starting from this index | 0 | [0,∞] |
| Facets.ValueFilter | String | Restrict values to those that start with the provided value (case sensitive) |  |  |
| Facets.ValueFilterOption.Contains | Boolean | Match also on results which contain the provided `valueFilter` at any point. e.g. Zea in New-Zealand. | false |  |
| Facets.ValueFilterOption.ContainsIgnoreCase | Boolean | Match on the provided `valueFilter` in a case-insensitive manner if `Facets.ValueFilterOption.Contains` is true. | false |  |
| Facets.Sort.Order | Enum | On what a facet is sorted. Possible values are `MostFrequent`, `Alphabetically`, `Chronologically`, `FixedOrder` | as configured in [Facet definition](#facet_definition_object) |  |
| Facets.Sort.ReverseOrder | Boolean | Sort the results in reverse order. Can only be true if Sort = `Chronologically` | as configured in [Facet definition](#facet_definition_object) |  |
| Facets.SelectionType | Enum | The type of selection. `SHOULD`: at least one selected value must match. `MUST`: all selected values must match | as configured in [Facet definition](#facet_definition_object) |  |
| Facets.Selection.Values | String[] | List of already selected non-missing facet values (Values.Value property of [Facet](#facet_result_object_legacy)). |  |  |
| Facets.Selection.Missing | Boolean | True if the missing value is selected (not applicable for date facets) | false |

Notes:
- Combination of Selection.Values and Selection.Missing = true is only supported for SelectionType = SHOULD (because selecting the missing value AND a specific value can impossibly yield results when the SelectionType is MUST).
- For date facets, only one value can be selected (with SelectionType = MUST).
- For facets with selection type `SHOULD`, the following applies: if a facet value is selected, this will affect the counts of all facets, except the facet itself.
- The following rules apply to the Facets.Sort property:
- Order value `Alphabetically` is not applicable for date facets
- Order value `Chronologically` is only applicable for date facets and corresponds with the [facet definition](#facet_definition_object) Sort property value `Alphabetically` for facets with Type `Date`
- Order value `FixedOrder` is only applicable for enum facets and corresponds with the [facet definition](#facet_definition_object) Sort property value `Enum` for facets with Type `Enum`: values are sorted in the order in which the possible values are defined on the field definition.
- `Facets.ValueFilter` and `Facets.ValueFilterOption` is not applicable for fields of type DateField, LongField, FramesField and BooleanField.
- When `Facets.ValueFilter` is not empty, the missing value for that facet is never returned.
- The following rules apply when requesting a specific facet:
- `Facets.SelectionType` and `Facets.Selection` are applicable for the specific facet and for other already selected facets.
- Other `Facets` properties are only applicable for the requested facet itself.
- `IncludeFilteredOnly` is always true.
- If `IncludeProfileFacetsOnly` is false and the facet profile does not contain the requested facet, a facet configuration with default values is used. The default values are the same as used in [facet profile properties](#profile_field_facet_properties)
- With the introduction of the parameter `profileId`, the properties `IncludeMissingValue` and `IncludeEmptyFacets` are only relevant for facets that are not configured in the facet profile. In other cases, these values are determined per facet within the facet profile, namely by the properties `IncludeMissingValue` and `HideEmpty`.

```json
{
  "Q": "+(*:*)",
  "Locale": "nl_BE",
  "Facets": [
    {
      "DottedKey": "Descriptive.Keywords.Keyword",
      "NrOfResults": 10,
      "StartIndex": 0,
      "ValueFilter": "KEYWORD",
      "ValueFilterOption": {
        "Contains": true,
        "ContainsIgnoreCase": true
      },
      "SelectionType": "SHOULD",
      "Selection": {
        "Values": ["cat", "dog"],
        "Missing": false
      },
      "Sort": {
        "Order": "Alphabetically",
        "ReverseOrder": false
      }
    }
  ],
  "IncludeMissingValue": false,
  "IncludeActiveValues": true,
  "ProfileId": "104ae264-3d4c-46cb-b02d-b6641289655c",
  "IncludeProfileFacetsOnly": false
}
```

### Facet definition object (legacy) {#facet_definition_object}

| Property | Type | Description |
| --- | --- | --- |
| DottedKey | String | The fully qualified key of the field on which the facet is based |
| Order | Number | The order of the facet |
| Type | Enum | The type of a facet. Possible values are Default, Enum or Date |
| DefaultNumberOfValues | Number | The number of facets to show |
| EnumOrder | String | The order in which the enums are sorted within a facet |
| IndexName | String | The index name of a facet |
| HideEmpty | Boolean | Indicates if the empty facets are hidden |
| Sort | Enum | On what a facet is sorted. Possible values are MostFrequent, Alphabetically or Enum |
| ReverseOrder | Boolean | Whether to sort in reverse order. Can only be true if Sort = Alphabetically and Type = Date |
| SelectionType | Enum | The type of selection. `SHOULD`: at least one selected value must match. `MUST`: all selected values must match |
| IncludeMissingValue | Boolean | Include the missing value (e.g. `No Keywords`). |

> Note: For facets with selection type `SHOULD`, the following applies: if a facet value is selected, this will affect the counts of all facets, except the facet itself.

```json
[
  {
    "DottedKey": "Descriptive.DepartmentName",
    "Order": 1,
    "Type": "Default",
    "DefaultNumberOfValues": 10,
    "EnumOrder": null,
    "IndexName": "mh-dev",
    "HideEmpty": false,
    "Sort": "MostFrequent",
    "ReverseOrder": false,
    "SelectionType": "MUST",
    "IncludeMissingValue": true
  },
  {
    "DottedKey": "Descriptive.Categories.Category",
    "Order": 2,
    "Type": "Default",
    "DefaultNumberOfValues": 10,
    "EnumOrder": null,
    "IndexName": "mh-dev",
    "HideEmpty": false,
    "Sort": "MostFrequent",
    "ReverseOrder": false,
    "SelectionType" : "SHOULD",
    "IncludeMissingValue": false
  },
  {
    "DottedKey": "Technical.ImageQuality",
    "Order": 3,
    "Type": "Enum",
    "DefaultNumberOfValues": 10,
    "EnumOrder": "high,medium,low",
    "IndexName": "mh-dev",
    "HideEmpty": false,
    "Sort": "Enum",
    "ReverseOrder": false,
    "SelectionType": "SHOULD",
    "IncludeMissingValue": true
  }
]
```

### Facet result object {#facet_result_object}

| Property | Type | Description | Default value |
| --- | --- | --- | --- |
| DottedKey | String | The fully qualified key of the field on which the facet is based. |  |
| Label | String | The translation of the field based on the requested locale or the locale of the user. |  |
| HasMoreValues | Boolean | Indicates whether more facet values are available beyond those returned, based on the requested start index and a fixed limit of 100. Additional values may exist beyond this limit. |  |
| Values | Values[] | A list of facet values. |  |
| Values.Value | String | The value of the facet. |  |
| Values.Label | String | The translation of the facet value, if no translation exists it equals the facet value. |  |
| Values.Count | Number | The number of records having this value. |  |
| Values.Missing | Boolean | Indicates if the facet value corresponds with the missing / empty facet value. |  |
| Values.Begin | Date | The begin date of the value (only applicable for date facets). |  |
| Values.End | Date | The end date of the value. Not included in the interval (only applicable for date facets). |  |
| Values.IncludeBegin | Boolean | Whether the begin itself is included (only applicable for date facets). | True |
| Values.IncludeEnd | Boolean | Whether the end itself is included (only applicable for date facets). | False |
| Values.Gap | Enum | The size of the gap between start and end. Possible values are `Year`, `Month` and `Day` (only applicable for date facets). | `Year` |

```json
[
  {
    "DottedKey": "Descriptive.Keywords.Keyword",
    "Label": "Trefwoord",
    "HasMoreValues": true,
    "Values": [
      {
        "Value": "Cork",
        "Label": "Cork",
        "Count": 423,
        "Missing": false
      },
      {
        "Value": "Dublin",
        "Label": "Dublin",
        "Count": 58,
        "Missing": false
      },
      {
        "Value": "No keyword",
        "Label": "Geen trefwoord",
        "Count": 9871,
        "Missing": true
      }
    ]
  },
  {
    "DottedKey": "Descriptive.CreationDate",
    "Label": "Datum inhoud",
    "Count": 987,
    "Values": [
      {
        "Value": "[2000-12-31T23:00:00.000000Z TO 2001-12-31T23:00:00.000000Z}",
        "Label": "2001",
        "Count": 193,
        "Missing": false,
        "Begin": "2000-12-31T23:00:00.000000Z",
        "End": "2001-12-31T23:00:00.000000Z",
        "IncludeBegin": true,
        "IncludeEnd": false,
        "Gap": "Year"
      }
    ]
  }
]
```

### Facet request object (Preferred) {#facet_request_object_preferred}

| Property | Type | Description | Default value |
| --- | --- | --- | --- |
| Search.StructuredQuery | [StructuredQuery](#structured_query_object) | Restrict to facets based on records matching the structured query, can be empty. |  |
| Locale.Value | String | Use this locale for translation of the labels and restrict facets if desired (see property `Locale.Restricted`). | user locale |
| Locale.Restricted | Boolean | Restrict to facets having the requested locale language or having no language property. If Locale is not set, the user locale is used. | false |
| Source.ProfileId | String | Return the facets based on the fields specified in the facet profile with this id. Can not be used together with `Source.CustomFacets`. | if `Source.CustomFacets` is not set, id of facet profile with tag `Default.Facet` |
| Source.CustomFacets | String[] | Return the facets based on the explicitly provided list of facet fields, where the values are dotted keys. Can not be used together with `Source.ProfileId`. |  |
| Value.Options.<DottedKey> | [Value Options](#facet_value_options_object)[] | Configure the behavior and presentation of facet values for the specified dotted key. These options override [facet profile field](#create_profile_field_facet_properties) properties when a `Source.ProfileId` is provided. |  |
| Value.Constraints.<DottedKey> | [Value Constraints](#facet_value_constraints_object)[] | Restrict facet values for this dotted key to those that meet the specified constraints. |  |
| Advanced.Debug | Boolean | Whether to log all available debug information about the SOLR request. Requires `ADMIN_BACKEND_SERVICES` to change. | false |
| Advanced.MinSemanticScore | Float | The minimum score for semantic query results. Requires `ADMIN_BACKEND_SERVICES` to change. | Dependent on plugin |

`Search.StructuredQuery.Facets` can be used, for example, to define which facet values are already selected for a facet field.
When dealing with date facets, and a facet is selected, the values in the response will drill one level deeper depending on the granularity of the selected facet.

For example:
- If you select a facet with `Gap = Year`, the response will show facets on a monthly level.
- If `Gap = Month` is selected, the response will show facets on a daily level.
- If `Gap = Year` is selected, no further facets will be shown, as the day is the lowest granularity level for this type of facet.

Note that only the first selected `RangeValue` in the list of `RangeBuckets` is taken into account.

```json
{
  "Search": {
    "StructuredQuery": {
      "Global": [
        "Alice",
        "Bob",
        "Cedric"
      ],
      "Facets": [
        {
          "LogicalOperand": "Or",
          "DottedKey": "Descriptive.Keywords.Keyword",
          "Buckets": [
            {
              "Operand": "Include",
              "Value": "New-Zealand"
            },
            {
              "Operand": "Exclude",
              "Value": "*"
            }
          ]
        }
      ],
      "Predefined" : [
        "Administrative.RecordStatus:Published"
      ]
    }
  },
  "Locale": {
    "Value": "nl_BE",
    "Restricted": false
  },
  "Source": {
    "ProfileId": "104ae264-3d4c-46cb-b02d-b6641289655c"
  },
  "Value": {
    "Options": {
      "Descriptive.Keywords.Keyword" : {
        "SelectionType": "SHOULD",
        "HideEmpty": false,
        "Sort": "Alphabetically",
        "ReverseOrder": false,
        "DefaultNumberOfValues": 5,
        "IncludeMissingValue": true,
        "IncludeActiveValues": false
      }
    },
    "Constraints" : {
      "Descriptive.Keywords.Keyword" : {
        "Prefix": "New",
        "Contains": "land",
        "ContainsIgnoreCase": true
      }
    }
  }
}
```

### Facet value options object {#facet_value_options_object}

| Property | Type | Description | Default Value |
| --- | --- | --- | --- |
| SelectionType | Enum | The type of selection. `SHOULD`: at least one selected value must match. `MUST`: all selected values must match. | MUST |
| HideEmpty | Boolean | Indicates if facets without values are hidden. | false |
| Sort | Enum | How the facet values are sorted. Possible values are `MostFrequent`, `Alphabetically`, `Chronologically`, `FixedOrder`. | depends on the field definition type |
| ReverseOrder | Boolean | Sort the values in reverse order. Can only be true if Sort = `Chronologically`. | false |
| DefaultNumberOfValues | Number | The number of facet values to show, excluding the missing value. Must be in range [1,100]. | 10 |
| IncludeMissingValue | Boolean | Include the missing value (e.g. `No Keywords`). | true |
| IncludeActiveValues | Boolean | Include values which are present in the [Bucket](#sq_facet_bucket_object) of the [structured query](#structured_query_object). Has no effect on date facets. | false |

Notes:
- For facets with `SelectionType` = `SHOULD`, the following applies: if a facet value is selected, this will affect the counts of all facets, except the facet itself.
- The missing value will never be included in following cases:
- Facet is a date field
- Missing value does not match with constraints defined in `Value.Constraints`
- `IncludeActiveValues` is true and the missing value is already selected (the missing value will never be shown in that case).
- The following rules apply to the `Sort` property:
- Value `Alphabetically` is not applicable for date facets
- Value `Chronologically` is only applicable for date facets
- Value `FixedOrder` is only applicable for enum facets. The values are sorted in the order in which the possible values are defined on the corresponding field definition.
- Default value for date fields is `Chronologically`, for enum fields `FixedOrder` and for others `MostFrequent`.

```json
{
  "SelectionType": "SHOULD",
  "HideEmpty": false,
  "Sort": "Alphabetically",
  "ReverseOrder": false,
  "DefaultNumberOfValues": 5,
  "IncludeMissingValue": true,
  "IncludeActiveValues": false
}
```

### Facet value constraints object {#facet_value_constraints_object}

| Property | Type | Description | Default value |
| --- | --- | --- | --- |
| Prefix | String | Limits the values to those starting with the given string prefix (case sensitive). |  |
| StartIndex | Number | Used for pagination, facet values will be returned starting from this index | 0 |

Notes:
- `Prefix` is not applicable for fields of type `DateField`, `LongField`, `FramesField` and `BooleanField`.
- When `Prefix` is defined for a facet, the missing value for that facet is never returned.
- The sum of value constraint `StartIndex` and value option `DefaultNumberOfValues` must not exceed 100

```json
{
  "Prefix": "New",
  "StartIndex": 5
}
```

## Task facets {#task_facets}

Currently, this resource is only available via the path “/workflow/api/tasks/facets”.

Faceted search categorizes and groups tasks by specific fields, with each facet representing a field and
showing the count of results for each distinct value. The response for each requested facet includes a list of values
that match the provided query and filter criteria.

The difference between the [facets on records](#facet_search) and facets on tasks, is that a single record can have
multiple tasks associated with it and this endpoint counts and returns tasks not records.
Hence, if a record has the keyword “XYZ” and 3 tasks linked with it, then the facet bucket on the keyword “XYZ” will
have its `Count` incremented by 3 if the search includes the record in question. However, if the search or selection
restricts it to for example certain task types, then only the matching tasks of the record will be included.

### Searching using POST {#task_facets_post}

To search for facets, send a `POST` request to:

```http
POST https://<your installation>/workflow/api/tasks/facets
```

With body [task tacet request](#task_facets_request). Notice that this request is highly similar to the
[record facet request](#facet_request_object_preferred), when the exception of the extra property “OnlyCompletable”.

#### Response

- `200` JSON Array of [Facet result](#facet_result_object)
- `400` The request contains invalid properties
- `403` User is not authorized
- `404` The profile ID could not be found

### Facet request object {#task_facets_request}

| Property | Type | Description | Default value |
| --- | --- | --- | --- |
| Search.StructuredQuery | [StructuredQuery](#structured_query_object) | Restrict to facets based on records matching the structured query, can be empty. |  |
| Search.OnlyCompletable | Boolean | Restrict to only tasks that can be completed by the current user. | `true` |
| Locale.Value | String | Use this locale for translation of the labels and restrict facets if desired (see property `Locale.Restricted`). | user locale |
| Locale.Restricted | Boolean | Restrict to facets having the requested locale language or having no language property. If Locale is not set, the user locale is used. | false |
| Source.ProfileId | String | Return the facets based on the fields specified in the facet profile with this id. Can not be used together with `Source.CustomFacets`. | if `Source.CustomFacets` is not set, id of facet profile with tag `Default.Facet` |
| Source.CustomFacets | String[] | Return the facets based on the explicitly provided list of facet fields, where the values are dotted keys. Can not be used together with `Source.ProfileId`. |  |
| Value.Options.<DottedKey> | [Value Options](#facet_value_options_object)[] | Configure the behavior and presentation of facet values for the specified dotted key. These options override [facet profile field](#create_profile_field_facet_properties) properties when a `Source.ProfileId` is provided. |  |
| Value.Constraints.<DottedKey> | [Value Constraints](#facet_value_constraints_object)[] | Restrict facet values for this dotted key to those that meet the specified constraints. |

> Note: `StructuredQuery.Facets` can be used, for example, to define which facet values are already selected for a facet field

```json
{
  "Search": {
    "StructuredQuery": {
      "Global": ["Dossier XYZ"]
    },
    "OnlyCompletable": true
  },
  "Locale": {
    "Value": "nl_BE",
    "Restricted": false
  },
  "Source": {
    "ProfileId": "104ae264-3d4c-46cb-b02d-b6641289655c"
  },
  "Value": {
    "Options": {
      "Descriptive.Keywords.Keyword": {
        "SelectionType": "SHOULD",
        "HideEmpty": false,
        "Sort": "Alphabetically",
        "ReverseOrder": false,
        "DefaultNumberOfValues": 5,
        "IncludeMissingValue": true,
        "IncludeActiveValues": false
      }
    },
    "Constraints": {
      "Descriptive.Keywords.Keyword": {
        "Prefix": "New"
      }
    }
  }
}
```

## Versionings {#versioning}

From version 2.0 and onwards the mediahaven-rest-api supports the creation of versions of records.
Each version starts with the status DRAFT. This object is not visible in the default search. To make it visible you will have to ACCEPT the draft or in case you don’t want to accept the DRAFT you can REJECT it.
The current active version will have the status HEAD. Older versions will have the status TAIL.

A versioned record-object will always have the following readonly-fields:

| Property | Type | Description |
| --- | --- | --- |
| VersioningId | String | Grouping-id of versioned Records. The value is shared across all records belonging to the same versioning chain. This value is the RecordId of the first record of the chain. |
| VersioningStatus | Enum | The status of this version (DRAFT, HEAD, REJECTED or TAIL) |
| VersioningVersion | Number | Version number that increases with each newly created draft |

Important to note is that only one version can be DRAFT and only one version can be HEAD.

From version `25.4` the property `PreserveId` is no longer in use and will be ignored by the request.

### Modules {#mediahaven-rest-api-manual-versionings-modules}

The `VERSION_MANAGEMENT` [module plugin](#modules) must always be active to use version management.

### Create draft {#edit_field_basics}

A draft can be created in 2-ways.

Take into account that only one draft for a specific versioningId can exist.

#### A new version of an existing versioned mediaobject {#create_existing_version}

To create a new (draft) version on an existing version you can send a POST request to the following endpoints:

```
https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId
https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId/versions/draft
```

The endpoint supports json and xml with the following properties

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Metadata | [Sidecar](#sidecar_format) | The metadata you want on the new version (if no metadata is provided for a specific value the value of the previous version will be used) | empty | no |
| Options | [Options](#versionings_options_format) | With this you can provide the event-subtype and reason of creation of new draft for audit logging | Object with default values. | no |
| AutoAccept | Boolean | Should the new version be accepted automatically | false | no |
| TailMetadata | [Sidecar](#sidecar_format) | The metadata you want to old version to have (can be useful to update a status field). This field can only be used during ACCEPT | empty | no |

Example:

```json
{
  "Metadata": {
    "Dynamic": {
      "TestField": "testValue"
    }
  },
  "Options": {
    "SubType": "VERSIONING.DRAFT",
    "Reason": "Creation of new draft"
  },
  "AutoAccept": true
}
```

The response will be a [Record](#record-object).

#### Options {#versionings_options_format}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| SubType | String | With this you can provide the event-subtype for audit logging | Empty | no |
| Reason | String | With this you can provide the reason of creation of new draft for audit logging | Empty | no |

#### Create a new versioned mediaobject from an existing mediaobject {#create_new_version}

```http
https://archief.viaa.be/mediahaven-rest-api/v2/versionings
```

The following properties are allowed on this endpoint

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| RecordId | String | The RecordId of the record you want to version | empty | yes |
| VersionId | String | The version the mediaobject should be linked to | empty | no |
| Options | [Options](#versionings_options_format) | With this you can provide the event-subtype and reason of creation of new draft for audit logging | Object with default values. | no |
| AutoAccept | Boolean | Should the new version be accepted automatically | false | no |

Example:

```json
{
  "RecordId": "f9101a58fcea4832a385e3cd15d2a359eb010268eb524a139a32b56116b4149d",
  "VersionId": "b44470ffc73a43c48866121858fbb56c76047f370e8549b692a3e5ca523892fa",
  "Options": {
    "SubType": "VERSIONING.DRAFT",
    "Reason": "Creation of new draft"
  },
  "AutoAccept": true
}
```

### Updating a draft {#update_draft}

Updating a draft can be done by sending a PUT-request to a specific draft (also possible by sending a PUT request on the media endpoint).

```http
https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId/versions/draft
```

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Metadata | [Sidecar](#sidecar_format) | The metadata you want to update | empty | no |
| DraftAction | Enum (ACCEPT, REJECT) | The action you want to execute on the draft (see further) | empty | yes |
| Options | [Options](#versionings_options_format) | With this you can provide the event-subtype and reason of creation of new draft for audit logging | Object with default values. | no |
| TailMetadata | [Sidecar](#sidecar_format) | The metadata you want to old version to have (can be useful to update a status field). This field can only be used during ACCEPT | empty | no |

Example:

```json
{
  "Metadata": { "Descriptive": { "Title": "new title" } }
}
```

#### Accept/reject a draft {#accept_or_reject_draft}

A draft can be accepted or rejected by sending a PUT-request to the specific draft with the draftAction filled in.
DraftAction can be **ACCEPT** or **REJECT**

It’s also possible to sent [options](#versionings_options_format) with it for audit-logging

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId/versions/draft
```

Example:

```json
{
  "DraftAction": "ACCEPT",
  "Options": {
    "SubType": "VERSIONING.DRAFT",
    "Reason": "Creation of new draft"
  }
}
```

### Getting a specific version {#specific_version}

Getting a specific version is done by sending a GET-request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId/versions/:versionId
```

There are also some predefined terms you can use to get a version

- **latest**: always returns the latest version (draft,head) `https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId/versions/latest`
- **head**: returns the current active version `https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId/versions/head`
- **draft**: returns the current draft version or a not-found error if there’s no draft `https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId/versions/draft`

In case the version does not exists a `404` response will be returned

### Searching versions {#search_versions}

Searching for versions has the same parameters as searching for a mediaobject

| Query parameter | Description | Default value | Required |
| --- | --- | --- | --- |
| q | Query you want to use to filter the results | empty | no |
| nrOfResults | The number of results you want to have per page | 25 | no |
| startIndex | The startIndex of the result | 0 | no |
| sort | The field on which should be sorted | empty | no |
| direction | The sort-direction for the sorting-field | empty | no |

The result is paged, for more info see [Paged result](#page).

Searching for versions can be done in 2-ways.

#### On a specific VersioningId {#specific_versioningId}

Sending a GET-request to the following endpoint

```http
https://archief.viaa.be/mediahaven-rest-api/v2/versionings/:versioningId
```

This endpoint will default sort on the version-field in a descending order.

#### All versions {#all_version}

Sending a GET-request to the following endpoint

```http
https://archief.viaa.be/mediahaven-rest-api/v2/versionings
```

This endpoint will only return the activeVersions but this can be changed by adding the following to your query

```
+(VersioningStatus:Draft VersioningStatus:Tail VersioningStatus:Head)
```

## Deleting records {#deleting}

Deleting a record will change the value of the `Administrative.DeleteStatus` field of the record. By default, this field
has the value `NotDeleted`.

A standard delete will set the status to `LogicallyDeleted`. As long as a record has this status, the deletion can be
reverted using the [update endpoint](#edit_metadata).

Relations are permanently removed upon logical deletion and previously related records are updated to reflect this
change. When the deletion of the record is reverted these relations are not restored.

After a certain period has passed, the deletion becomes permanent. By default, this happens after 180 days. In the
future this value will become configurable. When this happens, the status is set to `PermanentlyDeleted`. Soon
afterwards (depending on the system, by default within 24 hours) the file belonging to the record is deleted.

### Deleting a record {#deleting}

To remove a record, make a `DELETE` request to the following URL:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id
```

Deletes are idem potent. This means that when the same request is repeated multiple times, no error will be thrown. This
applies to both logical and permanent deletions.

Extra parameters can be provided via an optional [request body](#record_delete_object).

> Note: The request body is optional.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Reason | String | The reason why the record is deleted | empty string | no |
| EventType | String | A custom Subtype for the delete event | PERMANENTLY_DELETED if permanent, otherwise empty string. | no |
| Permanent | Boolean | Permanently remove the record. Only allowed for deletion status `LogicallyDeleted`. | false | no |

#### Response

- `204` No content
- `403` Forbidden: User can’t delete record, an appropriate [error result](#error) is returned.
- `404` Not found: an appropriate [error result](#error) is returned.

#### Authorization functions

- The function ‘RECYCLE_RECORDS’ is required to permanently delete a record.

#### Deleting a record JSON {#record_delete_object}

```json
{
  "Reason": "deprecated record",
  "EventType": "OBSOLETE",
  "Permanent": false
}
```

#### Deleting a record XML {#record_delete_object}

```xml
<DeleteRecord>
    <Reason>test reason</Reason>
    <EventType>test event type</EventType>
    <Permanent>false</Permanent>
</DeleteRecord>
```

### Restoring a deleted record {#undeleting}

This will set the field `Administrative.DeleteStatus` to `NotDeleted`. You can use the same endpoint as
when [updating a record](#edit_field_XML).

When using FormData, the following parameters can be used:

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| undelete | Boolean | Must be set to true to indicate you whish to restore the record. |  | Yes |
| reason | String | The reason why the record is restored. | empty string | no |
| eventType | String | A custom Subtype for the undelete event. | UNDELETE | no |

You can also use a [json](#record_undelete_object) or [xml](#record_undelete_object) request body.

This action is not compatible with the other properties on the update endpoint.

#### Response

- `204` No content
- `403` Forbidden: User can’t restore record.
- `404` Not found.
- `409` Conflict: `Administrative.DeleteStatus` is not set to `LogicallyDeleted`.

#### Authorization functions

- ‘RECYCLE_RECORDS’

#### Restoring a record JSON {#record_undelete_object}

```json
{
  "Undelete": true,
  "Reason": "Deleted by mistake",
  "EventType": "UNDO"
}
```

#### Deleting a record XML {#record_undelete_object_xml}

```xml
<?xml version="1.0" encoding="UTF-8"?>
<UpdateRecord>
    <Undelete>true</Undelete>
    <Reason>Deleted by mistake</Reason>
    <EventType>UNDO</EventType>
</UpdateRecord>
```

## Record format {#metadata}

### Sidecar Metadata 26.1 format {#sidecar_format}

When [uploading/creating](#uploading) or [editing](#edit_metadata) records, you can supply a sidecar XML file or sidecar
JSON file. Information about the structure of this file can be found
on [Metadata Sidecar 26.1](https://mediahaven.atlassian.net/wiki/display/CS/Metadata+Sidecar+26.1)
.

Here you can find the namespace definitions, validation XSDs and example XMLs.

> Note: you can also use ‘head’ instead of the current version (e.g. 26.1) in URLs or namespace definitions. This will always point to the latest available Metadata Sidecar version.

The format is designed in such manner each output Sidecar XML/JSON is perfectly valid as input. So for additional
examples of how to structure the XML you can export an existing record with its corresponding sidecar metadata.

When using the Sidecar XML/JSON as input for [upload](#uploading) or [metadata edit](#edit_field_XML), only the writable
fields are taken into account. Other fields will be ignored.

#### Context

When requesting a record in JSON or MHS format you will receive a `Context`-object. This object contains specific info
for the authenticated user and is not changeable. Following information is exposed in this object:

- Actions the authenticated user can do on this object
- ‘Reasons’ object which contains the reasons why one or more actions are not possible
- [Profiles](#profiles) linked to this record
- `Score` the score of the result

The equivalent `application/json` is

```json
{
  "IsEditable": "true",
  "IsDeletable": "true",
  "IsPublic": "false",
  "IsExportable" : "false",
  "IsPublishable": "false",
  "Reasons": {
    "IsPublishable": [
      {
        "Code": "RecordStatusNotPublishable",
        "Value": "Record can not be published in its current status"
      }
    ]
  },
  "Profiles": ["b9f25e12-8e49-11eb-8dcd-0242ac130003"]
}
```

A reason always contains a code and value. Possible codes are:
- `NoWriteRights`
- `NoPublishRights`
- `HasIntellectualParent`
- `RecordStatusNotPublishable`

The value contains a human readable description of the setting in English.

#### Example code

##### Sample MHS XML metadata {#sample_mhs_xml}

Single record:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mhs:Sidecar xmlns:mhs="https://zeticon.mediahaven.com/metadata/head/mhs/"
             xmlns:mh="https://zeticon.mediahaven.com/metadata/head/mh/"
             version="<head>">
    <mhs:Descriptive>
        <mh:Description strategy="KEEP">Un nouveau dinosaure a été découvert en Argentine ! ...</mh:Description>
        <mh:Keywords strategy="MERGE">
            <mh:Keyword>Argentine</mh:Keyword>
            <mh:Keyword>News</mh:Keyword>
            <mh:Keyword>Paléontologie</mh:Keyword>
            <mh:Keyword>RTL</mh:Keyword>
        </mh:Keywords>
    </mhs:Descriptive>
    <mhs:Dynamic>
        <OcariFRCollection>RTL Actu (489965)</OcariFRCollection>
        <VideoLink>http://vod-mp4.rtl.be/XXXXXXX.mp4</VideoLink>
        <OcariFRTopic>belgique</OcariFRTopic>
        <Permalink>XYZ</Permalink>
    </mhs:Dynamic>
    <mhs:Technical>
        <mh:Md5>8bdd0c5dc3ea6640e1553351edb45d87</mh:Md5>
    </mhs:Technical>
</mhs:Sidecar>
```

When returned by [search](#search-for-media-objects):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <NrOfResults>1</NrOfResults>
    <StartIndex>0</StartIndex>
    <TotalNrOfResults>1</TotalNrOfResults>
    <Results>
        <mhs:Sidecar xmlns:mh="https://zeticon.mediahaven.com/metadata/21.3/mh/"
                     xmlns:mhs="https://zeticon.mediahaven.com/metadata/21.3/mhs/"
                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="21.3"
                     xsi:schemaLocation="https://zeticon.mediahaven.com/metadata/21.3/mhs/ https://zeticon.mediahaven.com/metadata/21.3/mhs.xsd https://zeticon.mediahaven.com/metadata/21.3/mh/ https://zeticon.mediahaven.com/metadata/21.3/mh.xsd">
            <mhs:Descriptive>
                <mh:CreationDate>2021-07-01T18:41:33.000000Z</mh:CreationDate>
                <mh:UploadedBy>REST TEST</mh:UploadedBy>
                <mh:KeyframeStart>0000000000</mh:KeyframeStart>
                <mh:OriginalFilename>rest-test-01.mp4</mh:OriginalFilename>
                <mh:Title>rest-test-01.mp4</mh:Title>
                <mh:RightsOwner>SoundHandler</mh:RightsOwner>
            </mhs:Descriptive>
            <mhs:Administrative>
                <mh:LastModifiedDate>2021-07-01T18:47:06.381000Z</mh:LastModifiedDate>
                <mh:IsSynchronized>false</mh:IsSynchronized>
                <mh:IsOriginal>false</mh:IsOriginal>
                <mh:OrganisationName>develop</mh:OrganisationName>
                <mh:IsPreservation>false</mh:IsPreservation>
                <mh:DepartmentName>rest-api-test</mh:DepartmentName>
                <mh:UserLastModifiedDate>2021-07-01T18:41:39.899000Z</mh:UserLastModifiedDate>
                <mh:ArchiveDate>2021-07-01T18:41:33.689000Z</mh:ArchiveDate>
                <mh:OrganisationLongName>develop</mh:OrganisationLongName>
                <mh:RecordType>Record</mh:RecordType>
                <mh:RecordStatus>Published</mh:RecordStatus>
                <mh:IsAccess>false</mh:IsAccess>
                <mh:PublicationDate>2021-07-01T18:41:33.679000Z</mh:PublicationDate>
                <mh:DeleteStatus>NotDeleted</mh:DeleteStatus>
                <mh:Type>video</mh:Type>
                <mh:OrganisationExternalId>develop</mh:OrganisationExternalId>
            </mhs:Administrative>
            <mhs:Technical>
                <mh:ImageQuality>low</mh:ImageQuality>
                <mh:AudioTechnical>aac 2ch 44100Hz 705600bps</mh:AudioTechnical>
                <mh:VideoTechnical>h264 640x360 25fps 442644bps</mh:VideoTechnical>
                <mh:AudioTracks>
                    <mh:Track>
                        <mh:Channels>2</mh:Channels>
                        <mh:Language>spa</mh:Language>
                    </mh:Track>
                </mh:AudioTracks>
                <mh:PronomId>fmt/199</mh:PronomId>
                <mh:OriginalExtension>mp4</mh:OriginalExtension>
                <mh:AudioCodec>aac</mh:AudioCodec>
                <mh:AudioSampleRate>44100</mh:AudioSampleRate>
                <mh:DurationFrames>0000015000</mh:DurationFrames>
                <mh:VideoCodec>h264</mh:VideoCodec>
                <mh:FileSize>33818018</mh:FileSize>
                <mh:ImageSize>640x360</mh:ImageSize>
                <mh:EndFrames>0000015000</mh:EndFrames>
                <mh:MimeType>video/mp4</mh:MimeType>
                <mh:DurationTimeCode>00:10:00.000</mh:DurationTimeCode>
                <mh:StartFrames>0000000000</mh:StartFrames>
                <mh:Height>360</mh:Height>
                <mh:EndTimeCode>00:10:00.000</mh:EndTimeCode>
                <mh:Width>640</mh:Width>
                <mh:Md5>2bcffb8692eecc986535ed9e4c9f8042</mh:Md5>
                <mh:AudioBitRate>705600</mh:AudioBitRate>
                <mh:StartTimeCode>00:00:00.000</mh:StartTimeCode>
                <mh:VideoBitRate>442644</mh:VideoBitRate>
                <mh:ImageOrientation>landscape</mh:ImageOrientation>
                <mh:AudioChannels>2</mh:AudioChannels>
                <mh:VideoFps>25</mh:VideoFps>
                <mh:BitRate>450886</mh:BitRate>
            </mhs:Technical>
            <mhs:Internal>
                <mh:PathToVideo>
                    https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758/browse.mp4
                </mh:PathToVideo>
                <mh:OriginalStatus>completed</mh:OriginalStatus>
                <mh:PathToKeyframe>
                    https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758/keyframes/keyframes_1_1/keyframe1.jpg
                </mh:PathToKeyframe>
                <mh:IsFragment>false</mh:IsFragment>
                <mh:UploadedById>d16652c1-beea-415d-b307-888910c93aea</mh:UploadedById>
                <mh:HasKeyframes>true</mh:HasKeyframes>
                <mh:Browses>
                    <mh:Browse>
                        <mh:BaseUrl>
                            https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758
                        </mh:BaseUrl>
                        <mh:PathToKeyframe>keyframes/keyframes_1_1/keyframe1.jpg</mh:PathToKeyframe>
                        <mh:PathToKeyframeThumb>keyframes-thumb/keyframes_1_1/keyframe1.jpg</mh:PathToKeyframeThumb>
                        <mh:PathToVideo>browse.mp4</mh:PathToVideo>
                        <mh:HasKeyframes>true</mh:HasKeyframes>
                        <mh:Container>mp4</mh:Container>
                        <mh:Label>mp4</mh:Label>
                        <mh:FileSize>75886885</mh:FileSize>
                        <mh:AudioTracks>
                            <mh:Track>
                                <mh:Channels>2</mh:Channels>
                            </mh:Track>
                        </mh:AudioTracks>
                        <mh:Height>360</mh:Height>
                        <mh:VideoCodec>h264</mh:VideoCodec>
                        <mh:Width>640</mh:Width>
                        <mh:AudioChannels>2</mh:AudioChannels>
                        <mh:AudioCodec>aac</mh:AudioCodec>
                        <mh:BitRate>1011739</mh:BitRate>
                        <mh:AudioSampleRate>22050</mh:AudioSampleRate>
                        <mh:VideoBitRate>1005775</mh:VideoBitRate>
                        <mh:AudioBitRate>352800</mh:AudioBitRate>
                        <mh:VideoFps>25</mh:VideoFps>
                    </mh:Browse>
                    <mh:Browse>
                        <mh:BaseUrl>
                            https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758
                        </mh:BaseUrl>
                        <mh:PathToVideo>peak-0.json</mh:PathToVideo>
                        <mh:HasKeyframes>false</mh:HasKeyframes>
                        <mh:Container>peak</mh:Container>
                        <mh:Label>peak-0</mh:Label>
                        <mh:FileSize>24108</mh:FileSize>
                        <mh:BitRate>8</mh:BitRate>
                        <mh:AudioSampleRate>10</mh:AudioSampleRate>
                        <mh:AudioCodec>audiowaveform</mh:AudioCodec>
                    </mh:Browse>
                </mh:Browses>
                <mh:MediaObjectId>0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758</mh:MediaObjectId>
                <mh:ArchiveStatus>on_disk</mh:ArchiveStatus>
                <mh:BrowseStatus>completed</mh:BrowseStatus>
                <mh:RecordId>0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758</mh:RecordId>
                <mh:IsInIngestSpace>true</mh:IsInIngestSpace>
                <mh:IngestSpaceId>1341da3b-241e-42bf-af52-748127c22309</mh:IngestSpaceId>
                <mh:OrganisationId>100</mh:OrganisationId>
                <mh:FragmentId>
                    0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875844fe312a066c40d0ac98ef5c83675b59
                </mh:FragmentId>
                <mh:PathToKeyframeThumb>
                    https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758/keyframes-thumb/keyframes_1_1/keyframe1.jpg
                </mh:PathToKeyframeThumb>
                <mh:ContainsGeoData>false</mh:ContainsGeoData>
                <mh:DepartmentId>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:DepartmentId>
            </mhs:Internal>
            <mhs:Structural>
                <mh:FragmentEndTimeCode>00:10:00.000</mh:FragmentEndTimeCode>
                <mh:Fragments>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887583511fd8bdfc440a2a4257ddeabdfb01d
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887587b6e460bb38547f994433a3e092dfabb
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887586a0ca8bd0ac2476e8a88cb8f20c51785
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875878dc3263b49d4eddae71dd18454818e7
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875897d714cea3cb47558c6b6c0027706f95
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758fc7e0ea5dc1f4ff99cfd986975687fbe
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887581d104478a4f74284a3768045b9955f0a
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758a14be20fcda94bfab7ece6ded872a3ae
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887582b2b53a102b6462286dbd5db869645c6
                    </mh:Fragment>
                    <mh:Fragment>
                        0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758396cb0efd0944c95bea0d47731cd143d
                    </mh:Fragment>
                </mh:Fragments>
                <mh:HasChildren>false</mh:HasChildren>
                <mh:FragmentStartFrames>0000000000</mh:FragmentStartFrames>
                <mh:FragmentDurationFrames>0000015000</mh:FragmentDurationFrames>
                <mh:FragmentDurationTimeCode>00:10:00.000</mh:FragmentDurationTimeCode>
                <mh:FragmentStartTimeCode>00:00:00.000</mh:FragmentStartTimeCode>
                <mh:FragmentEndFrames>0000015000</mh:FragmentEndFrames>
                <mh:Versioning>
                    <mh:Version>0000000001</mh:Version>
                    <mh:Status>Untracked</mh:Status>
                </mh:Versioning>
            </mhs:Structural>
            <mhs:RightsManagement>
                <mh:Permissions>
                    <mh:Write>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Write>
                    <mh:Write>e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Write>
                    <mh:Write>da100b7a-efd0-44e3-8816-0905572421da</mh:Write>
                    <mh:Export>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Export>
                    <mh:Export>e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Export>
                    <mh:Export>da100b7a-efd0-44e3-8816-0905572421da</mh:Export>
                    <mh:Read>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Read>
                    <mh:Read>e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Read>
                    <mh:Read>da100b7a-efd0-44e3-8816-0905572421da</mh:Read>
                </mh:Permissions>
                <mh:Zone>
                    <mh:Id>1341da3b-241e-42bf-af52-748127c22309</mh:Id>
                    <mh:Name>MediaHaven 2.0 Concepts</mh:Name>
                </mh:Zone>
                <mh:RecordPhase>Published</mh:RecordPhase>
            </mhs:RightsManagement>
            <Context>
                <IsEditable>true</IsEditable>
                <IsDeletable>true</IsDeletable>
                <IsExportable>true</IsExportable>
                <IsEmbeddable>true</IsEmbeddable>
                <IsPublishable>false</IsPublishable>
                <Reasons>
                    <IsPublishable>
                        <Code>RecordStatusNotPublishable</Code>
                        <Value>Record can not be published in its current status</Value></Value>
                    </IsPublishable>    
                </Reasons>
                <Profiles>
                    <Profile>b9f25e12-8e49-11eb-8dcd-0242ac130003</Profile>
                </Profiles>
            </Context>
        </mhs:Sidecar>
    </Results>
</Response>
```

##### Sample Dublin Core XML metadata {#sample_dc_xml}

Single record:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
    <dc:title>rest-test-09.png</dc:title>
    <dc:date>2021-07-01</dc:date>
    <dc:type>image/png</dc:type>
    <dc:rights>© DEVELOP</dc:rights>
    <dc:identifier>cef05c84d37a43e6bc50fa563dc86d701e8c2a4ea7ca4d0f9e2b485d1516b47788c1d38bb76a4bdbb18405f3b9bd62ec
    </dc:identifier>
</oai_dc:dc>
```

When returned by [search](#search-for-media-objects):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <NrOfResults>1</NrOfResults>
    <StartIndex>0</StartIndex>
    <TotalNrOfResults>1</TotalNrOfResults>
    <Results>
        <oai_dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
            <dc:title>rest-test-09.png</dc:title>
            <dc:date>2021-07-01</dc:date>
            <dc:type>image/png</dc:type>
            <dc:rights>© DEVELOP</dc:rights>
            <dc:identifier>
                cef05c84d37a43e6bc50fa563dc86d701e8c2a4ea7ca4d0f9e2b485d1516b47788c1d38bb76a4bdbb18405f3b9bd62ec
            </dc:identifier>
        </oai_dc:dc>
    </Results>
</Response>
```

##### Sample METS MHS XML metadata {#sample_mets_mhs_xml}

Single record:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mets:mets xmlns:mets="http://www.loc.gov/METS/" xmlns:premis="premis-2.xsd"
           xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd premis-2.xsd premis-2.xsd">
    <mets:metsHdr CREATEDATE="2021-07-01T18:41:33Z"
                  ID="MEDIAHAVEN_0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875844fe312a066c40d0ac98ef5c83675b59"
                  LASTMODDATE="2021-07-01T18:47:06.381000Z">
        <mets:agent ROLE="CREATOR" TYPE="ORGANIZATION">
            <mets:name>MEDIAHAVEN</mets:name>
        </mets:agent>
        <mets:agent ROLE="CUSTODIAN" TYPE="ORGANIZATION">
            <mets:name>zeticon</mets:name>
        </mets:agent>
        <mets:agent ROLE="IPOWNER" TYPE="ORGANIZATION">
            <mets:name>develop</mets:name>
        </mets:agent>
    </mets:metsHdr>
    <mets:dmdSec
            ID="DMDID-Record-0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875844fe312a066c40d0ac98ef5c83675b59">
        <mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="mhs:Sidecar">
            <mets:xmlData>
                <mhs:Sidecar xmlns:mh="https://zeticon.mediahaven.com/metadata/head/mh/"
                             xmlns:mhs="https://zeticon.mediahaven.com/metadata/head/mhs/" version="head"
                             xsi:schemaLocation="https://zeticon.mediahaven.com/metadata/head/mhs/ https://zeticon.mediahaven.com/metadata/head/mhs.xsd https://zeticon.mediahaven.com/metadata/head/mh/ https://zeticon.mediahaven.com/metadata/head/mh.xsd">
                    <mhs:Descriptive>
                        <mh:CreationDate>2021-07-01T18:41:33.000000Z</mh:CreationDate>
                        <mh:UploadedBy>REST TEST</mh:UploadedBy>
                        <mh:KeyframeStart>0000000000</mh:KeyframeStart>
                        <mh:OriginalFilename>rest-test-01.mp4</mh:OriginalFilename>
                        <mh:Title>rest-test-01.mp4</mh:Title>
                        <mh:RightsOwner>SoundHandler</mh:RightsOwner>
                    </mhs:Descriptive>
                    <mhs:Administrative>
                        <mh:LastModifiedDate>2021-07-01T18:47:06.381000Z</mh:LastModifiedDate>
                        <mh:IsSynchronized>false</mh:IsSynchronized>
                        <mh:IsOriginal>false</mh:IsOriginal>
                        <mh:OrganisationName>develop</mh:OrganisationName>
                        <mh:IsPreservation>false</mh:IsPreservation>
                        <mh:DepartmentName>rest-api-test</mh:DepartmentName>
                        <mh:UserLastModifiedDate>2021-07-01T18:41:39.899000Z</mh:UserLastModifiedDate>
                        <mh:ArchiveDate>2021-07-01T18:41:33.689000Z</mh:ArchiveDate>
                        <mh:OrganisationLongName>develop</mh:OrganisationLongName>
                        <mh:RecordType>Record</mh:RecordType>
                        <mh:RecordStatus>Published</mh:RecordStatus>
                        <mh:IsAccess>false</mh:IsAccess>
                        <mh:PublicationDate>2021-07-01T18:41:33.679000Z</mh:PublicationDate>
                        <mh:DeleteStatus>NotDeleted</mh:DeleteStatus>
                        <mh:Type>video</mh:Type>
                        <mh:OrganisationExternalId>develop</mh:OrganisationExternalId>
                    </mhs:Administrative>
                    <mhs:Technical>
                        <mh:ImageQuality>low</mh:ImageQuality>
                        <mh:AudioTechnical>aac 2ch 44100Hz 705600bps</mh:AudioTechnical>
                        <mh:VideoTechnical>h264 640x360 25fps 442644bps</mh:VideoTechnical>
                        <mh:AudioTracks>
                            <mh:Track>
                                <mh:Channels>2</mh:Channels>
                                <mh:Language>spa</mh:Language>
                            </mh:Track>
                        </mh:AudioTracks>
                        <mh:PronomId>fmt/199</mh:PronomId>
                        <mh:OriginalExtension>mp4</mh:OriginalExtension>
                        <mh:AudioCodec>aac</mh:AudioCodec>
                        <mh:AudioSampleRate>44100</mh:AudioSampleRate>
                        <mh:DurationFrames>0000015000</mh:DurationFrames>
                        <mh:VideoCodec>h264</mh:VideoCodec>
                        <mh:FileSize>33818018</mh:FileSize>
                        <mh:ImageSize>640x360</mh:ImageSize>
                        <mh:EndFrames>0000015000</mh:EndFrames>
                        <mh:MimeType>video/mp4</mh:MimeType>
                        <mh:DurationTimeCode>00:10:00.000</mh:DurationTimeCode>
                        <mh:StartFrames>0000000000</mh:StartFrames>
                        <mh:Height>360</mh:Height>
                        <mh:EndTimeCode>00:10:00.000</mh:EndTimeCode>
                        <mh:Width>640</mh:Width>
                        <mh:Md5>2bcffb8692eecc986535ed9e4c9f8042</mh:Md5>
                        <mh:AudioBitRate>705600</mh:AudioBitRate>
                        <mh:StartTimeCode>00:00:00.000</mh:StartTimeCode>
                        <mh:VideoBitRate>442644</mh:VideoBitRate>
                        <mh:ImageOrientation>landscape</mh:ImageOrientation>
                        <mh:AudioChannels>2</mh:AudioChannels>
                        <mh:VideoFps>25</mh:VideoFps>
                        <mh:BitRate>450886</mh:BitRate>
                    </mhs:Technical>
                    <mhs:Internal>
                        <mh:PathToVideo>
                            https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758/browse.mp4
                        </mh:PathToVideo>
                        <mh:OriginalStatus>completed</mh:OriginalStatus>
                        <mh:PathToKeyframe>
                            https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758/keyframes/keyframes_1_1/keyframe1.jpg
                        </mh:PathToKeyframe>
                        <mh:IsFragment>false</mh:IsFragment>
                        <mh:UploadedById>d16652c1-beea-415d-b307-888910c93aea</mh:UploadedById>
                        <mh:HasKeyframes>true</mh:HasKeyframes>
                        <mh:Browses>
                            <mh:Browse>
                                <mh:BaseUrl>
                                    https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758
                                </mh:BaseUrl>
                                <mh:PathToKeyframe>keyframes/keyframes_1_1/keyframe1.jpg</mh:PathToKeyframe>
                                <mh:PathToKeyframeThumb>keyframes-thumb/keyframes_1_1/keyframe1.jpg
                                </mh:PathToKeyframeThumb>
                                <mh:PathToVideo>browse.mp4</mh:PathToVideo>
                                <mh:HasKeyframes>true</mh:HasKeyframes>
                                <mh:Container>mp4</mh:Container>
                                <mh:Label>mp4</mh:Label>
                                <mh:FileSize>75886885</mh:FileSize>
                                <mh:AudioTracks>
                                    <mh:Track>
                                        <mh:Channels>2</mh:Channels>
                                    </mh:Track>
                                </mh:AudioTracks>
                                <mh:Height>360</mh:Height>
                                <mh:VideoCodec>h264</mh:VideoCodec>
                                <mh:Width>640</mh:Width>
                                <mh:AudioChannels>2</mh:AudioChannels>
                                <mh:AudioCodec>aac</mh:AudioCodec>
                                <mh:BitRate>1011739</mh:BitRate>
                                <mh:AudioSampleRate>22050</mh:AudioSampleRate>
                                <mh:VideoBitRate>1005775</mh:VideoBitRate>
                                <mh:AudioBitRate>352800</mh:AudioBitRate>
                                <mh:VideoFps>25</mh:VideoFps>
                            </mh:Browse>
                            <mh:Browse>
                                <mh:BaseUrl>
                                    https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758
                                </mh:BaseUrl>
                                <mh:PathToVideo>peak-0.json</mh:PathToVideo>
                                <mh:HasKeyframes>false</mh:HasKeyframes>
                                <mh:Container>peak</mh:Container>
                                <mh:Label>peak-0</mh:Label>
                                <mh:FileSize>24108</mh:FileSize>
                                <mh:BitRate>8</mh:BitRate>
                                <mh:AudioSampleRate>10</mh:AudioSampleRate>
                                <mh:AudioCodec>audiowaveform</mh:AudioCodec>
                            </mh:Browse>
                        </mh:Browses>
                        <mh:MediaObjectId>0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758
                        </mh:MediaObjectId>
                        <mh:ArchiveStatus>on_disk</mh:ArchiveStatus>
                        <mh:BrowseStatus>completed</mh:BrowseStatus>
                        <mh:RecordId>0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758</mh:RecordId>
                        <mh:IsInIngestSpace>false</mh:IsInIngestSpace>
                        <mh:OrganisationId>100</mh:OrganisationId>
                        <mh:FragmentId>
                            0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875844fe312a066c40d0ac98ef5c83675b59
                        </mh:FragmentId>
                        <mh:PathToKeyframeThumb>
                            https://develop.mediahaven.com/DEVELOP/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758/keyframes-thumb/keyframes_1_1/keyframe1.jpg
                        </mh:PathToKeyframeThumb>
                        <mh:ContainsGeoData>false</mh:ContainsGeoData>
                        <mh:DepartmentId>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:DepartmentId>
                    </mhs:Internal>
                    <mhs:Structural>
                        <mh:FragmentEndTimeCode>00:10:00.000</mh:FragmentEndTimeCode>
                        <mh:Fragments>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887583511fd8bdfc440a2a4257ddeabdfb01d
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887587b6e460bb38547f994433a3e092dfabb
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887586a0ca8bd0ac2476e8a88cb8f20c51785
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875878dc3263b49d4eddae71dd18454818e7
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875897d714cea3cb47558c6b6c0027706f95
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758fc7e0ea5dc1f4ff99cfd986975687fbe
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887581d104478a4f74284a3768045b9955f0a
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758a14be20fcda94bfab7ece6ded872a3ae
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c57887582b2b53a102b6462286dbd5db869645c6
                            </mh:Fragment>
                            <mh:Fragment>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758396cb0efd0944c95bea0d47731cd143d
                            </mh:Fragment>
                        </mh:Fragments>
                        <mh:HasChildren>false</mh:HasChildren>
                        <mh:FragmentStartFrames>0000000000</mh:FragmentStartFrames>
                        <mh:FragmentDurationFrames>0000015000</mh:FragmentDurationFrames>
                        <mh:FragmentDurationTimeCode>00:10:00.000</mh:FragmentDurationTimeCode>
                        <mh:FragmentStartTimeCode>00:00:00.000</mh:FragmentStartTimeCode>
                        <mh:FragmentEndFrames>0000015000</mh:FragmentEndFrames>
                        <mh:Versioning>
                            <mh:Version>0000000001</mh:Version>
                            <mh:Status>Untracked</mh:Status>
                        </mh:Versioning>
                    </mhs:Structural>
                    <mhs:RightsManagement>
                        <mh:Permissions>
                            <mh:Write>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Write>
                            <mh:Write>e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Write>
                            <mh:Write>da100b7a-efd0-44e3-8816-0905572421da</mh:Write>
                            <mh:Export>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Export>
                            <mh:Export>e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Export>
                            <mh:Export>da100b7a-efd0-44e3-8816-0905572421da</mh:Export>
                            <mh:Read>d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Read>
                            <mh:Read>e451bf9f-aaf3-43b2-bf0b-99bc9a361ff6</mh:Read>
                            <mh:Read>da100b7a-efd0-44e3-8816-0905572421da</mh:Read>
                        </mh:Permissions>
                        <mh:RecordPhase>Published</mh:RecordPhase>
                    </mhs:RightsManagement>
                </mhs:Sidecar>
            </mets:xmlData>
        </mets:mdWrap>
    </mets:dmdSec>
    <mets:amdSec
            ID="ADMID-Record-0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875844fe312a066c40d0ac98ef5c83675b59">
        <mets:digiprovMD ID="PREMISID-84">
            <mets:mdWrap MDTYPE="PREMIS:EVENT">
                <mets:xmlData>
                    <premis:event>
                        <premis:eventIdentifier>
                            <premis:eventIdentifierType>MEDIAHAVEN_EVENT</premis:eventIdentifierType>
                            <premis:eventIdentifierValue>84</premis:eventIdentifierValue>
                        </premis:eventIdentifier>
                        <premis:eventType>RECORDS.CREATE</premis:eventType>
                        <premis:eventDateTime>2021-07-01T18:41:33.689Z</premis:eventDateTime>
                        <premis:eventDetail/>
                        <premis:eventOutcomeInformation>
                            <premis:eventOutcome>OK</premis:eventOutcome>
                        </premis:eventOutcomeInformation>
                        <premis:linkingAgentIdentifier>
                            <premis:linkingAgentIdentifierType>MEDIAHAVEN_USER</premis:linkingAgentIdentifierType>
                            <premis:linkingAgentIdentifierValue>rest-api-test</premis:linkingAgentIdentifierValue>
                        </premis:linkingAgentIdentifier>
                        <premis:linkingObjectIdentifier>
                            <premis:linkingObjectIdentifierType>MEDIAHAVEN_ID</premis:linkingObjectIdentifierType>
                            <premis:linkingObjectIdentifierValue>
                                0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875844fe312a066c40d0ac98ef5c83675b59
                            </premis:linkingObjectIdentifierValue>
                        </premis:linkingObjectIdentifier>
                    </premis:event>
                </mets:xmlData>
            </mets:mdWrap>
        </mets:digiprovMD>
    </mets:amdSec>
    <mets:fileSec>
        <mets:fileGrp/>
    </mets:fileSec>
    <mets:structMap>
        <mets:div ADMID="PREMISID-84 PREMISID-85 PREMISID-115 PREMISID-116 PREMISID-166 PREMISID-167 PREMISID-168"
                  DMDID="DMDID-Record-0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c578875844fe312a066c40d0ac98ef5c83675b59"
                  TYPE="Record"/>
    </mets:structMap>
</mets:mets>
```

When returned by [search](#search-for-media-objects):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <NrOfResults>1</NrOfResults>
    <StartIndex>0</StartIndex>
    <TotalNrOfResults>1</TotalNrOfResults>
    <Results>
        <mets:mets xmlns:mets="http://www.loc.gov/METS/" xmlns:premis="http://www.loc.gov/premis/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd http://www.loc.gov/premis/v3 http://www.loc.gov/standards/premis/v3/premis.xsd">
            <mets:metsHdr CREATEDATE="2023-11-03T08:07:13Z" ID="MEDIAHAVEN_b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9139f4547ed5842b1bb6a8d0fa4198543" LASTMODDATE="2023-11-03T08:13:32.468000Z">
                <mets:agent ROLE="CREATOR" TYPE="ORGANIZATION">
                    <mets:name>MEDIAHAVEN</mets:name>
                </mets:agent>
                <mets:agent ROLE="CUSTODIAN" TYPE="ORGANIZATION">
                    <mets:name>zeticon</mets:name>
                </mets:agent>
                <mets:agent ROLE="IPOWNER" TYPE="ORGANIZATION">
                    <mets:name>mh-dev</mets:name>
                </mets:agent>
            </mets:metsHdr>
            <mets:dmdSec ID="DMDID-Record-b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9139f4547ed5842b1bb6a8d0fa4198543">
                <mets:mdWrap MDTYPE="OTHER" OTHERMDTYPE="mhs:Sidecar">
                    <mets:xmlData>
                        <mhs:Sidecar xmlns:mh="https://zeticon.mediahaven.com/metadata/24.1/mh/" xmlns:mhs="https://zeticon.mediahaven.com/metadata/24.1/mhs/" version="24.1" xsi:schemaLocation="https://zeticon.mediahaven.com/metadata/24.1/mhs/ https://zeticon.mediahaven.com/metadata/24.1/mhs.xsd https://zeticon.mediahaven.com/metadata/24.1/mh/ https://zeticon.mediahaven.com/metadata/24.1/mh.xsd">
                            <mhs:Descriptive>
                                <mh:UploadedBy>rest-api-test</mh:UploadedBy>
                                <mh:KeyframeStart>0000000000</mh:KeyframeStart>
                                <mh:OriginalFilename>UnpublishedTest5f686655-fcb4-4669-a074-8e676022b01c</mh:OriginalFilename>
                                <mh:Title>UnpublishedTest5f686655-fcb4-4669-a074-8e676022b01c</mh:Title>
                            </mhs:Descriptive>
                            <mhs:Administrative>
                                <mh:LastModifiedDate>2023-11-03T08:13:32.468000Z</mh:LastModifiedDate>
                                <mh:IsSynchronized>false</mh:IsSynchronized>
                                <mh:IsOriginal>false</mh:IsOriginal>
                                <mh:OrganisationName>mh-dev</mh:OrganisationName>
                                <mh:HasFailedJobs>false</mh:HasFailedJobs>
                                <mh:IsPreservation>false</mh:IsPreservation>
                                <mh:UserLastModifiedDate>2023-11-03T08:07:13.800000Z</mh:UserLastModifiedDate>
                                <mh:ArchiveDate>2023-11-03T08:07:13.800000Z</mh:ArchiveDate>
                                <mh:OrganisationLongName>mh-dev</mh:OrganisationLongName>
                                <mh:RecordType>Record</mh:RecordType>
                                <mh:RecordStatus>New</mh:RecordStatus>
                                <mh:IsAccess>false</mh:IsAccess>
                                <mh:DeleteStatus>NotDeleted</mh:DeleteStatus>
                                <mh:Type>metadataonly</mh:Type>
                                <mh:MainRecordType>Record</mh:MainRecordType>
                            </mhs:Administrative>
                            <mhs:Technical>
                                <mh:FileSize>1417252236</mh:FileSize>
                                <mh:MimeType>foo/bar</mh:MimeType>
                                <mh:Md5>daf3678cde38e2ed4112054588b46336</mh:Md5>
                            </mhs:Technical>
                            <mhs:Internal>
                                <mh:IndexName>mh-dev</mh:IndexName>
                                <mh:OriginalStatus>completed</mh:OriginalStatus>
                                <mh:PathToKeyframe>https://mheuropehot.blob.core.windows.net/mediahaven-saas-browse-main/no-preview.png</mh:PathToKeyframe>
                                <mh:IsFragment>false</mh:IsFragment>
                                <mh:PathToPreview>https://mheuropehot.blob.core.windows.net/mediahaven-saas-browse-main/no-preview.png</mh:PathToPreview>
                                <mh:UploadedById>8435e84c-2584-424d-8de6-70f98aa99013</mh:UploadedById>
                                <mh:IngestSpaceId>aa100ce7-51d6-41db-bf44-b085a4464c22</mh:IngestSpaceId>
                                <mh:HasKeyframes>false</mh:HasKeyframes>
                                <mh:MediaObjectId>b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9</mh:MediaObjectId>
                                <mh:ArchiveStatus>completed</mh:ArchiveStatus>
                                <mh:BrowseStatus>no_browse</mh:BrowseStatus>
                                <mh:RecordId>b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9</mh:RecordId>
                                <mh:IsInIngestSpace>true</mh:IsInIngestSpace>
                                <mh:OrganisationId>100</mh:OrganisationId>
                                <mh:FragmentId>b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9139f4547ed5842b1bb6a8d0fa4198543</mh:FragmentId>
                                <mh:OffsetInDatabase>425</mh:OffsetInDatabase>
                                <mh:PathToKeyframeThumb>https://mheuropehot.blob.core.windows.net/mediahaven-saas-browse-main/no-preview.png</mh:PathToKeyframeThumb>
                                <mh:ContainsGeoData>false</mh:ContainsGeoData>
                            </mhs:Internal>
                            <mhs:Structural>
                                <mh:RecordStructure>DataFlat</mh:RecordStructure>
                                <mh:HasChildren>false</mh:HasChildren>
                                <mh:HasNonRepresentationChildren>false</mh:HasNonRepresentationChildren>
                                <mh:Versioning>
                                    <mh:Version>0000000001</mh:Version>
                                    <mh:Status>Untracked</mh:Status>
                                </mh:Versioning>
                            </mhs:Structural>
                            <mhs:RightsManagement>
                                <mh:Permissions>
                                    <mh:Export>dd100b7a-efd0-44e3-8816-0905572421da</mh:Export>
                                    <mh:Export>da100b7a-efd0-44e3-8816-0905572421da</mh:Export>
                                    <mh:Export>76da9805-ccbd-4383-92fb-d2f6cf67282a</mh:Export>
                                    <mh:Write>dd100b7a-efd0-44e3-8816-0905572421da</mh:Write>
                                    <mh:Write>da100b7a-efd0-44e3-8816-0905572421da</mh:Write>
                                    <mh:Write>76da9805-ccbd-4383-92fb-d2f6cf67282a</mh:Write>
                                    <mh:Read>dd100b7a-efd0-44e3-8816-0905572421da</mh:Read>
                                    <mh:Read>de100b7a-efd0-44e3-8816-0905572421da</mh:Read>
                                    <mh:Read>df100b7a-efd0-44e3-8816-0905572421da</mh:Read>
                                    <mh:Read>da100b7a-efd0-44e3-8816-0905572421da</mh:Read>
                                    <mh:Read>76da9805-ccbd-4383-92fb-d2f6cf67282a</mh:Read>
                                </mh:Permissions>
                                <mh:RecordPhase>Concept</mh:RecordPhase>
                                <mh:Zone>
                                    <mh:Name>MediaHaven 2.0 Concepts</mh:Name>
                                    <mh:Id>aa100ce7-51d6-41db-bf44-b085a4464c22</mh:Id>
                                </mh:Zone>
                            </mhs:RightsManagement>
                            <mhs:Dynamic>
                                <GameFrameRate>0000054745</GameFrameRate>
                            </mhs:Dynamic>
                            <mhs:Timers>
                                <mh:Expiry>
                                    <mh:ExpectedDate>2011-01-01T00:00:00.000000Z</mh:ExpectedDate>
                                </mh:Expiry>
                            </mhs:Timers>
                        </mhs:Sidecar>
                    </mets:xmlData>
                </mets:mdWrap>
            </mets:dmdSec>
            <mets:amdSec ID="ADMID-Record-b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9139f4547ed5842b1bb6a8d0fa4198543">
                <mets:digiprovMD ID="PREMISID-2249">
                    <mets:mdWrap MDTYPE="PREMIS:EVENT">
                        <mets:xmlData>
                            <premis:event>
                                <premis:eventIdentifier>
                                    <premis:eventIdentifierType>MEDIAHAVEN_EVENT</premis:eventIdentifierType>
                                    <premis:eventIdentifierValue>2249</premis:eventIdentifierValue>
                                </premis:eventIdentifier>
                                <premis:eventType>RECORDS.CREATE</premis:eventType>
                                <premis:eventDateTime>2023-11-03T08:07:13.800Z</premis:eventDateTime>
                                <premis:eventDetailInformation>
                                    <premis:eventDetail/>
                                </premis:eventDetailInformation>
                                <premis:eventOutcomeInformation>
                                    <premis:eventOutcome>OK</premis:eventOutcome>
                                </premis:eventOutcomeInformation>
                                <premis:linkingAgentIdentifier>
                                    <premis:linkingAgentIdentifierType>MEDIAHAVEN_USER</premis:linkingAgentIdentifierType>
                                    <premis:linkingAgentIdentifierValue>rest-api-test</premis:linkingAgentIdentifierValue>
                                </premis:linkingAgentIdentifier>
                                <premis:linkingObjectIdentifier>
                                    <premis:linkingObjectIdentifierType>MEDIAHAVEN_ID</premis:linkingObjectIdentifierType>
                                    <premis:linkingObjectIdentifierValue>b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9139f4547ed5842b1bb6a8d0fa4198543</premis:linkingObjectIdentifierValue>
                                </premis:linkingObjectIdentifier>
                            </premis:event>
                        </mets:xmlData>
                    </mets:mdWrap>
                </mets:digiprovMD>
                <mets:digiprovMD ID="PREMISID-2250">
                    <mets:mdWrap MDTYPE="PREMIS:EVENT">
                        <mets:xmlData>
                            <premis:event>
                                <premis:eventIdentifier>
                                    <premis:eventIdentifierType>MEDIAHAVEN_EVENT</premis:eventIdentifierType>
                                    <premis:eventIdentifierValue>2250</premis:eventIdentifierValue>
                                </premis:eventIdentifier>
                                <premis:eventType>RECORDS.UPDATE</premis:eventType>
                                <premis:eventDateTime>2023-11-03T08:13:32.468Z</premis:eventDateTime>
                                <premis:eventDetailInformation>
                                    <premis:eventDetail/>
                                    <mhs:Difference xmlns:mhs="https://zeticon.mediahaven.com/metadata/24.1/mhs/">
                                        <mhs:MetadataFieldChange>
                                            <mhs:DottedKey>Dynamic.GameFrameRate</mhs:DottedKey>
                                            <mhs:ValueBefore/>
                                            <mhs:ValueAfter>0000054745</mhs:ValueAfter>
                                        </mhs:MetadataFieldChange>
                                        <mhs:MetadataFieldChange>
                                            <mhs:DottedKey>Structural.FragmentStartFrames</mhs:DottedKey>
                                            <mhs:ValueBefore/>
                                            <mhs:ValueAfter>0000000000</mhs:ValueAfter>
                                        </mhs:MetadataFieldChange>
                                        <mhs:MetadataFieldChange>
                                            <mhs:DottedKey>Structural.FragmentEndFrames</mhs:DottedKey>
                                            <mhs:ValueBefore/>
                                            <mhs:ValueAfter>0000000000</mhs:ValueAfter>
                                        </mhs:MetadataFieldChange>
                                        <mhs:MetadataFieldChange>
                                            <mhs:DottedKey>Timers.Expiry</mhs:DottedKey>
                                            <mhs:Expiry/>
                                            <mhs:Expiry>
                                                <mhs:ExpectedDate>2011-01-01T00:00:00.000000Z</mhs:ExpectedDate>
                                            </mhs:Expiry>
                                        </mhs:MetadataFieldChange>
                                    </mhs:Difference>
                                </premis:eventDetailInformation>
                                <premis:eventOutcomeInformation>
                                    <premis:eventOutcome>OK</premis:eventOutcome>
                                </premis:eventOutcomeInformation>
                                <premis:linkingAgentIdentifier>
                                    <premis:linkingAgentIdentifierType>MEDIAHAVEN_USER</premis:linkingAgentIdentifierType>
                                    <premis:linkingAgentIdentifierValue>zeticon@mh-dev</premis:linkingAgentIdentifierValue>
                                </premis:linkingAgentIdentifier>
                                <premis:linkingObjectIdentifier>
                                    <premis:linkingObjectIdentifierType>MEDIAHAVEN_ID</premis:linkingObjectIdentifierType>
                                    <premis:linkingObjectIdentifierValue>b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9139f4547ed5842b1bb6a8d0fa4198543</premis:linkingObjectIdentifierValue>
                                </premis:linkingObjectIdentifier>
                            </premis:event>
                        </mets:xmlData>
                    </mets:mdWrap>
                </mets:digiprovMD>
            </mets:amdSec>
            <mets:fileSec>
                <mets:fileGrp/>
            </mets:fileSec>
            <mets:structMap>
                <mets:div ADMID="PREMISID-2249 PREMISID-2250" DMDID="DMDID-Record-b885644505db4e7abf201d93a2a25c1afce1a8cbad9c43eab4c72d82d3463fb9139f4547ed5842b1bb6a8d0fa4198543" TYPE="Record"/>
            </mets:structMap>
        </mets:mets>
    </Results>
</Response>
```

##### Sample JSON metadata {#sample_json}

```json
{
  "MergeStrategies": {
    "Description": "KEEP",
    "Keywords": "MERGE"
  },
  "Descriptive": {
    "Description": "Un nouveau dinosaure a été découvert en Argentine ! ...",
    "Keywords": {
      "Keyword": [
        "Argentine",
        "News",
        "Paléontologie",
        "RTL"
      ]
    }
  },
  "Dynamic": {
    "OcariFRCollection": "RTL Actu (489965)",
    "VideoLink": "VideoLink",
    "OcariFRTopic": "Belgique",
    "Permalink": "XYZ"
  },
  "Technical": {
    "Md5": "8bdd0c5dc3ea6640e1553351edb45d87"
  }
}
```

### Sample record object {#record-object}

This is how a record can look like when retrieved via/during [searching](#search-for-media-objects)
, [creation](#uploading) or [editing](#edit_metadata). For a more detailed explanation,
consult [Metadata 26.1](https://mediahaven.atlassian.net/wiki/display/CS/Metadata+26.1)
Note that the exact structure can differ per installation. Contact your system administrator for more information.

```json
{
  "Administrative": {
    "ArchiveDate": "2020:01:14 20:20:21",
    "DepartmentName": "develop",
    "ExternalId": "develop_wc_zip",
    "IngestTape": null,
    "IsAccess": false,
    "IsOriginal": true,
    "IsPreservation": false,
    "IsSynchronized": false,
    "LastModifiedDate": "2020-01-14T19:20:21Z",
    "OrganisationLongName": "develop",
    "OrganisationName": "develop",
    "Type": "collection",
    "Workflow": null,
    "ChildOrderFields": {
      "Field": [
        {
          "DottedKey": "Descriptive.Title",
          "Direction": "asc"
        },
        {
          "DottedKey": "Administrative.ArchiveDate",
          "Direction": "desc"
        }
      ]
    }
  },
  "Context": {
    "IsDeletable": true,
    "IsEditable": true,
    "IsExportable": true,
    "IsPublic": true,
    "IsEmbeddable": true,
    "IsPublishable": false,
    "Reasons": {
      "IsPublishable": [
        {
          "Code": "RecordStatusNotPublishable",
          "Value": "Record can not be published in its current status"
        }
      ]
    },
    "Profiles": []
  },
  "Descriptive": {
    "Address": {},
    "Authors": {},
    "Categories": {
      "Category": []
    },
    "CreationDate": "2020:01:14 20:20:21",
    "Description": null,
    "KeyframeStart": 0,
    "Keywords": {
      "Keyword": []
    },
    "Location": null,
    "NonPreferredTerm": null,
    "OriginalFilename": "wc.zip",
    "Publications": null,
    "Publisher": null,
    "Rights": null,
    "RightsOwner": "© DEVELOP",
    "Title": "press conference",
    "UploadedBy": "Bulk Upload"
  },
  "Internal": {
    "ArchiveStatus": "in_progress",
    "BrowseStatus": "in_progress",
    "Browses": {
      "Browse": [
        {
          "BaseUrl": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277",
          "HasKeyframes": false,
          "PathToKeyframe": "browse.jpg",
          "PathToKeyframeThumb": "browse-thumb.jpg"
        }
      ]
    },
    "ContainsGeoData": false,
    "DepartmentId": "dd100b7a-efd0-44e3-8816-0905572421da",
    "FragmentId": "0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de654832ce77664161ab4d3f14b28247da",
    "HasKeyframes": false,
    "IngestSpaceId": null,
    "IsFragment": false,
    "IsInIngestSpace": false,
    "MediaObjectId": "0aa42d0a8edc41fab8cc88cad86c6f5558aa75768f1c4c5085a81cd3825427de",
    "OrganisationId": "100",
    "OriginalStatus": "in_progress",
    "PathToKeyframe": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277/browse.jpg",
    "PathToKeyframeThumb": "https://develop.mediahaven.com/DEVELOP/4f13432bebaf423280f7b9341c05ba0b67e05d4465be41bda532b55d3379c277/browse-thumb.jpg",
    "PathToVideo": null,
    "UploadedById": "ff100a7a-efd0-44e3-8816-0905572421da"
  },
  "RightsManagement": {
    "ExpiryDate": null,
    "ExpiryStatus": null,
    "Permissions": {
      "Export": [
        "dd100b7a-efd0-44e3-8816-0905572421da",
        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
        "da100b7a-efd0-44e3-8816-0905572421da"
      ],
      "Read": [
        "dd100b7a-efd0-44e3-8816-0905572421da",
        "de100b7a-efd0-44e3-8816-0905572421da",
        "df100b7a-efd0-44e3-8816-0905572421da",
        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
        "da100b7a-efd0-44e3-8816-0905572421da"
      ],
      "Write": [
        "dd100b7a-efd0-44e3-8816-0905572421da",
        "d451bf9f-aaf3-43b2-bf0b-99bc9a361ff6",
        "da100b7a-efd0-44e3-8816-0905572421da"
      ]
    }
  },
  "Structural": {
    "Collections": {
      "Collection": []
    },
    "FragmentDurationFrames": null,
    "FragmentDurationTimeCode": null,
    "FragmentEndFrames": null,
    "FragmentEndTimeCode": null,
    "FragmentStartFrames": null,
    "FragmentStartTimeCode": null,
    "Fragments": {},
    "Newspapers": {
      "Newspaper": []
    },
    "Relations": {},
    "Sets": {
      "Set": []
    },
    "Versioning": {
      "Status": "Untracked",
      "Version": 1
    },
    "PreviewRecordId": null
  },
  "Technical": {
    "AudioTechnical": null,
    "BitRate": null,
    "DurationFrames": null,
    "DurationTimeCode": null,
    "EndFrames": null,
    "EndTimeCode": null,
    "FileSize": 0,
    "Height": null,
    "ImageOrientation": null,
    "ImageQuality": null,
    "ImageSize": null,
    "Md5": null,
    "MimeType": null,
    "OriginalExtension": "zip",
    "PronomId": null,
    "StartFrames": null,
    "StartTimeCode": null,
    "VideoBitRate": null,
    "VideoCodec": null,
    "VideoFormat": null,
    "VideoFps": null,
    "VideoTechnical": null,
    "Width": null
  }
}
```

### Generating a QR code {#qr-code}

A QR code can be generated for each record by sending a `GET` request to following url

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/qr.(svg|jpg|png)
```

The QR code contains `<protocol>://<recordId>?<queryParamKey>=<queryParamValue>`
ex. `mediahaven://0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758?q1=abc&q2=def`

| Query parameter | Description | Default |
| --- | --- | --- |
| protocol | The protocol that should be used in the QR code | mediahaven |
| size | The size of the image, maximum 365, minimum 76 | 365 |
|  | Custom query parameter, with as value , that should be used in the QR code |

> Note: Any parameter other than `protocol` or `size` is considered as custom query parameter.

#### Response

- `200` A QR code in svg-format is returned
- `404` Record not found
- `400` Record id is not valid or the provided protocol is not correctly formatted

### Register consultation {#record-consult}

A consultation event can be added via `POST` request to following url

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/consult
```

Read access is necessary to be able to register event

| Query parameter | Description | Default |
| --- | --- | --- |
| type | type of consult ( ACCESS or ORIGINAL) | ACCESS |

#### Response

- `202` A consultation has been registered
- `404` Record not found
- `400` Record id is not valid or the provided protocol is not correctly formatted

### Register direct download {#record-direct-download}

A direct download event can be added via `POST` request to following url

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/direct-download
```

Read access is necessary to be able to register event

| Query parameter | Description | Default |
| --- | --- | --- |
| type | type of download ( ACCESS or ORIGINAL) | ACCESS |

#### Response

- `202` A direct download has been registered
- `404` Record not found
- `400` Record id is not valid or the provided protocol is not correctly formatted

## Similarity Search {#similarity_search}

Similarity search allows for requesting for an existing record, similar records based their content.
Under the hood it compares records based on a precalculated embeddings or keywords stored as metadata.
The returned records are restricted to the records to which the user has read rights and
excludes the record itself. The results are sorted based on descending similarity.

### Modules {#mediahaven-rest-api-manual-similarity-search-modules}

This feature is partly [modular](#modules) in the sense without any embedding module active, the similarity
search will only use similarity based on keywords.

### Getting similar objects {#similarity_search_get_all}

A list of similar objects can be retrieved using a `GET` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/similar
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`.
The standard [Page parameters](#page-filter) are available.

Note that the total number of results is limited to the first 100 objects. Specifying [Page parameters](#page-filter)
that bring the search beyond the first 100 objects, will result in a validation error.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default | Default Value |
| --- | --- | --- | --- |
| dottedKey | The dotted key of the field definition holding an embedding. | The field definition of type `VectorFieldDefinition` with the largest number of dimensions present on the record. If none are present, it falls back to similarity using `Descriptive.Keywords.Keyword`. |  |
| q | Same meaning as [basic searching](#basic-searching). See [query syntax](#query-syntax). |  |  |
| minimumScore | Float | The minimum similarity score required for a record to be included in the search results | 0.59 |
| fields | List | The fields that should be exposed in the result. Dotted keys are supported and `Score`,`Context` (Can be combined with profiles) | \* (all) |
| fieldsToExclude | List | The fields that should be excluded from the result (Can be combined with profiles and fields) | Ai.\* |
| profiles | List | The profiles for which the fields should be returned (Can be combined with fields) |

Following formats are supported:

- Json: `application/json` [Example](#record-object) **(default)**
- MHS_HEAD: `application/xml` [Example](#sample_mhs_xml)
- Dublin core: `application/dc+xml` [Example](#sample_dc_xml)
- METS_MHS_HEAD: `application/mets+mhs+xml` [Example](#sample_mets_mhs_xml)

#### Response

- `200` Ok. [Page](#page) of [Records](#record-object)
- `400` Going beyond the first 100 objects
- `400` There is no `VectorFieldDefinition` present on the record
- `400` The dotted key does not refer to a valid `VectorFieldDefinition`
- `400` The record does not have an embedding stored for the provided dotted key
- `404` The record does not exist or the user has no read rights to it

### Getting similar objects using POST {#similarity_search_post}

To search for similar records using a `POST` request, the following endpoint can be used:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/similar
```

The available properties and responses are equivalent
to [getting similar objects using GET](#similarity_search_get_all).
Note that the properties start with a capital letter in the JSON body.

#### Example JSON body {#search-request-obj-json}

```json
{
  "Q": "+Descriptive.Keywords.Keyword:Nature",
  "DottedKey": "Technical.Embeddings.MyAi4O",
  "NrOfResults": 50,
  "StartIndex": 0
}
```

## Metadata Field Definitions {#field_definitions}

### Introduction {#field_definitions_introduction}

Metadata is added to records in metadata fields. Fields can be client-specific, or can be general MediaHaven fields.
These fields contain all metadata ranging from (internal) technical information to domain-specific record information.

Not all metadata fields will be `indexed` (`searchable`). This is dependent on the specific installation configuration.
Some metadata fields will also be `readonly` and some will be `required` and cannot be empty.

Fields can also be structured in a parent-child relation. An excellent example is the Authors field:

- Authors
    - Creator : …
    - Writer : …
    - Composer : …

In order to properly parse the fields of a record, or validate metadata for updates, it will be useful to access the definitions of these fields.

#### Editing {#field_definitions_editing}

Modifying or adding field definitions is only possible in `Draft` mode.
Only fields with status `Published` are usable for metadata.
This allows you to prepare changes without having impact on existing data.

All changes need to be published via the [publish action](#publish_field_changes_action).
This action processes the changes asynchronous. You can track the status in `Draft` mode by filtering on the status `Processing`.

### Field types {#field_types}

See [Metadata concepts (external link)](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2703753301/Metadata+Field+Types)

Note that new types can be introduced in newer versions of MediaHaven.

### Getting a list of field definitions {#field_definitions_get_all}

A [Page](#page) of field definitions can be retrieved using a GET call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions
```

In addition to the standard pagination parameters, you can declare whether you want a flat list of definitions (with ID
references to parent and children), or if you want a nested parent-child structure.

| Query parameter | Type | Description | Default | required |
| --- | --- | --- | --- | --- |
| nested | Boolean | Include children and parents in the response (see response types) | `false` | no |
| profiles | array | List of profile id’s to filter the field definitions on |  | no |
| sort | String | Determine how to sort the field definitions | DottedKey | no |
| collapseLongTranslations | Enum(`FieldType`, `All`, `None`) | `FieldType`: Collapse long translations if type is `ListField` or `EnumMapField`, `All`: Also collapse if parent has same label, `None`: no collapsing | `FieldType` | no |
| indexName | String | The name of the index to search in | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the index name of the organisation of the current user | no |
| mode | Enum(`Production`, `Draft`) | If you want to edit fields you need to be in `Draft` mode | `Production` | no |
| status | Enum(`Draft`, `Processing`, `Published`) | When in `Draft` mode you can filter on status |  | no |
| search | String | Filter field definitions matching the partial search term in dotted key or translations in the user’s locale. Matching is case-insensitive and ignores whitespace. Wildcards \* are allowed |  | no |

The following attributes can be sorted on:

- DottedKey
- FieldDefinitionId `Deprecated, might be removed in the future.`
- LongTranslation, as determined by the locale of the user

#### Response

- `200` A [Page](#page) of either [Flat field definitions](#field_definition_flat_object)
  or [Nested field definitions](#field_definition_nested_object)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

#### Authorization functions

- Any authenticated user can access this resource
- Requesting field definitions of an index of a different organisation requires the ADMIN_VIEW_ALL_ORGANISATIONS function

### Retrieve a single field definition {#field_definitions_endpoint_single}

If you want to request the definition of a single field, you can make a GET call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey
```

Following query parameters are possible:

| Query parameter | Type | Description | Default | required |
| --- | --- | --- | --- | --- |
| nested | Boolean | Include children and parents in the response (see response types) | `false` | no |
| collapseLongTranslations | Enum(`FieldType`, `All`, `None`) | `FieldType`: Collapse long translations if type is `ListField` or `EnumMapField`, `All`: Also collapse if parent has same label, `None`: no collapsing | `FieldType` | no |
| mode | Enum(`Production`, `Draft`) | If you want to edit fields you need to be in `Draft` mode | `Production` | no |

> Note: Requesting a field definition by `fieldDefinitionId` or `flatKey` is deprecated, use `dottedKey` instead.

#### Response

- `200` Ok: A [Flat field definition](#field_definition_flat_object) or
  a [Nested field definition](#field_definition_nested_object) as requested
- `404` The field definition could not be found

#### Authorization functions

- Any authenticated user can access this resource
- Requesting field definitions of an index of a different organisation requires the ADMIN_VIEW_ALL_ORGANISATIONS function

### Creating a field definition {#field_definitions_create}

A field definition can be created by performing a `POST`-request
with [Field definition](#field_definition_object) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions
```

These changes are only visible in `Draft` mode. To publish the change call the [publish action](#publish_field_changes_action)
You can create any type, including [Nested field definitions](#field_definition_nested_object)

#### Response

- `201` The created [Flat field definition](#field_definition_flat_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function
- `429` Too many requests per minute

#### Authorization functions

- Using this endpoint requires the `ADMIN_FIELD_DEFINITIONS` function.
- Creating field definitions for an index of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Updating a field definition {#field_definitions_update}

Updating a field definition can be done by performing a `PUT`-request
with [Field definition](#field_definition_object) as body to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey
```

These changes are only visible in `Draft` mode. To publish the change call the [publish action](#publish_field_changes_action)
You can update any type, including [Nested field definitions](#field_definition_nested_object).

When using `Children` fields won’t be removed, manual deletion calls are necessary.

#### Response

- `200` Ok. Body: Updated [Flat field definition](#field_definition_flat_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the field definition or the field definition is not editable
- `404` The field definition could not be found
- `429` Too many requests per minute

#### Authorization functions

- Using this endpoint requires the `ADMIN_FIELD_DEFINITIONS` function.
- Updating field definitions for an index of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Deleting a field definition {#field_definitions_delete}

A field definition can be deleted by performing a `DELETE`-request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey
```

These changes are only visible in `Draft` mode. To publish the change call the [publish action](#publish_field_changes_action)

#### Response

- `204` The field definition was deleted
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the field definition or the field definition is not deletable
- `404` The field definition could not be found
- `429` Too many requests per minute

#### Authorization functions

- Using this endpoint requires the `ADMIN_FIELD_DEFINITIONS` function.
- Deleting field definitions for an index of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Publishing changes to field definitions {#publish_field_changes_action}

Changes to field definitions can be published by performing a `PUT`-request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/
```

The body must contain an [action object](#field_definition_action) with property `Action`=`PublishDrafts`

The changes are published asynchronously. You can track this by status of each field.

#### Response

- `200` Ok: A [Field definition action result object](#field_definition_action_result)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the action
- `409` Another change is already processing (code `FIELD-DEFINITIONS-PROCESSING`) or the subaction is not allowed (code `FIELD-DEFINITIONS-SUBACTION-NOT-ALLOWED`)

#### Authorization functions

- Using this endpoint requires the `ADMIN_FIELD_DEFINITIONS` function.
- Publishing field definitions for an index of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Reset pending changes to field definitions {#reset_pending_field_changes_action}

Pending changes to field definitions can be reset by performing a `PUT`-request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/
```

The body must contain an [action object](#field_definition_action) with property `Action`=`ResetDrafts`

As a result, field definitions with status `Processing` are reset to status `Draft`.
Note that this is a recovery action and should only be used when the publication needs to be retried in case of asynchronous errors.

#### Response

- `200` Ok: A [Field definition action result object](#field_definition_action_result)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the action

#### Authorization functions

- Using this endpoint requires the `ADMIN_FIELD_DEFINITIONS` and `ADMIN_BACKEND_SERVICES` function.
- Resetting field definitions for an index of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Field definition object structure {#field_definition_object}

#### Default properties {#field_definition_default_properties}

Properties applicable for each field type:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Key | String | The key of the Field definition. | yes, after creation |  | yes |
| FlatKey | String | The flat key of The field definition. | yes |  |  |
| DottedKey | String | The fully qualified key separated by dots. | yes |  |  |
| FieldDefinitionId | String | `Deprecated property, might be removed in the future.` The id of the field definition. | yes |  |  |
| ParentId | Number | `Deprecated property, might be removed in the future.` The FieldDefinitionId of the parent field definition. | yes |  |  |
| ParentDottedKey | String | The DottedKey of the parent field definition. | yes, after creation |  |  |
| Family | String | The [family](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2699657412/Metadata+Families) of the FieldDefinition. | yes, after creation | Dynamic |  |
| Translations | Map | The different translations for the field definition. |  |  |  |
| Translations > (language) | String | `Deprecated property, might be removed in the future.` The translation in the given language. |  | value of Key property |  |
| Translations > (locale) | String | The translation for the given local, if not defined, a fallback will be used. |  | value of Key property |  |
| LongTranslations | Map | The translation prepended with the parents’ translation (separated by “>”) | yes |  |  |
| LongTranslations > (language) | String | `Deprecated property, might be removed in the future.` The translation in the given language. | yes |  |  |
| LongTranslations > (locale) | String | The translation for the given locale, if not defined, a fallback will be used. | yes |  |  |
| Type | [FieldType](#field_types) | The type of the field. |  | SimpleField | yes |
| Searchable | Boolean | Whether the field can be used in search queries. |  | false |  |
| FullText | Boolean | Whether the field can be used in full text search |  | false |  |
| GlobalSearch | Boolean | Whether the field can be used in global search. |  | false |  |
| AdvancedSearch | Boolean | Whether the field can be used in advanced search. |  | false |  |
| Sortable | Boolean | Whether the field can be sorted on. |  | false |  |
| Inheritance | Enum (None, Creation, Propagation) | Type of inheritance this FieldDefinition follows |  | None |  |
| ReadOnly | Boolean | Whether the field can be updated. |  | false |  |
| WriteOnce | Boolean | Whether the field becomes readonly after first write |  | false |  |
| Required | Boolean | Whether the field can be assigned an empty value. |  | false |  |
| MultiValued | Boolean | Whether this field can have multiple values due to being nested. | yes | false |  |
| IndexName | String | The name of the index the field belongs to. If null, the field is available in all indices. |  | null |  |
| ChangeType | Enum(`Delete`,`Create`, `Update`) | When in draft mode this field displays the type of change | yes |  |  |
| Status | Enum(`Draft`,`Processing`, `Published`) | When the field is `Processing` it’s no longer editable. Only `Published` fields are usable for ingestion | yes |  |  |
| Version | Number | The version of this field | yes |  |  |
| Initiator | Enum(`System`,`Migration`, `User`) | Who initiated the change to a field. User changes are always `User` | yes |  |  |
| Context.IsEditable | Boolean | Whether the field definition is editable. | yes |  |  |
| Context.IsDeletable | Boolean | Whether the field definition is deletable. | yes |  |  |
| Context.HasEditableChildren | Boolean | Whether children can be added to or removed from the field definition. | yes |  |

Notes:
- The field `LongTranslations` contains both the translations of the parent field definition(s) and the field
  definition itself, delimited by a `>`.
- A translation is provided for each supported locale. If no translation is defined for a specific locale, a fallback will be used, namely the first non-empty value from the following list:
- The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
- The translation for the ‘overall’ default locale `en_US`
- The key of the field definition
- Information about the field `Inheritance` can be found.
  on [Metadata Inheritance](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2656043129/Metadata+Inheritance).
- All GlobalSearch fields are represented by a preconfigured field `Global`, which allows the user to search for a
  value without specifying the exact field.
- A field definition always belongs to 1 index OR all indices. On creation/update, IndexName can be set to NULL
  to make the field definition accessible to all indices.
- A field can only be sortable if it is searchable and if its (main) type is equal to SimpleField.

```json
{
  "Key": "Title",
  "FlatKey": "Title",
  "DottedKey": "Descriptive.Title",
  "FieldDefinitionId": 1,
  "ParentId": null,
  "ParentDottedKey": "",
  "Family": "Descriptive",
  "Translations": {
    "nl_BE": "Titel BE",
    "nl_NL": "Titel NL",
    "fr_BE": "Titre",
    "en_US": "Title",
    "en": "Title",
    "fr": "Titre",
    "nl": "Titel BE"
  },
  "Type": "SimpleField",
  "Searchable": true,
  "FullText": false,
  "ReadOnly": false,
  "Required": true,
  "GlobalSearch": true,
  "AdvancedSearch": true,
  "Sortable": true,
  "Inheritance": "Propagation",
  "LongTranslations": {
    "nl_BE": "Titel BE",
    "nl_NL": "Titel NL",
    "fr_BE": "Titre",
    "en_US": "Title",
    "en": "Title",
    "fr": "Titre",
    "nl": "Titel BE"
  },
  "IndexName": "indexName",
  "Context": {
    "IsEditable": false,
    "IsDeletable": false,
    "HasEditableChildren": false
  }
}
```

#### ThesaurusField properties {#field_definition_thesaurus_properties}

Properties only applicable for type `ThesaurusField`:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Scheme.Id | String | The identifier of this thesaurus scheme. |  |  | yes, if applies to one index |
| Scheme.ExternalThesaurusId | String | Identifier of the thesaurus. | yes |  |  |
| Scheme.Name | String | The name of the thesaurus. |  |  | yes, if applies to all indices |
| Scheme.TopConcept | String | The uri of the top concept. | yes |  |  |
| Scheme.MinNarrower | Number | Minimum depth of child that can be selected. | yes |  |  |
| Scheme.MaxNarrower | Number | Maximum depth of child that can be selected. | yes |  |  |
| Languages | Array | List of languages |  | All languages |

When providing the `Languages` the system will automatically create the necessary `ThesaurusLabelField`s and `ThesaurusUriField`

```json
{
  "Key": "ThesaurusTest",
  "FlatKey": "ThesaurusTest",
  "DottedKey": "Dynamic.ThesaurusTest",
  "FieldDefinitionId": 60041,
  "ParentId": null,
  "ParentDottedKey": "",
  "Family": "Dynamic",
  "Translations": {
    "nl_BE": "ThesaurusTest",
    "en_US": "Thesaurus Test",
    "fr_BE": "ThesaurusTest",
    "en": "Thesaurus Test",
    "fr": "ThesaurusTest",
    "nl": "ThesaurusTest"
  },
  "Type": "ThesaurusField",
  "Searchable": true,
  "ReadOnly": false,
  "Required": false,
  "GlobalSearch": false,
  "AdvancedSearch": false,
  "Sortable": false,
  "Inheritance": "None",
  "LongTranslations": {
    "nl_BE": "ThesaurusTest",
    "en_US": "Thesaurus Test",
    "fr_BE": "ThesaurusTest",
    "en": "Thesaurus Test",
    "fr": "ThesaurusTest",
    "nl": "ThesaurusTest"
  },
  "IndexName": "indexName",
  "Scheme": {
    "Id": "784a2b17-ac28-495f-93f5-8647181ac059",
    "ExternalThesaurusId": "3f148ec0-2a24-4e33-97d8-7d80537be071",
    "Name": "Collection hobbies",
    "TopConcept": "https://dev.mediahaven.com/thesaurus/_f6765036",
    "MinNarrower": 1,
    "MaxNarrower": 1
  }
}
```

#### ThesaurusLabelField properties {#field_definition_thesauruslabel_properties}

Properties only applicable for type `ThesaurusLabelField`:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Lang | String | The language of the field. |  |  |

```json
{
  "Key": "Nl",
  "FlatKey": "ThesaurusTestNl",
  "DottedKey": "Dynamic.ThesaurusTest.Nl",
  "FieldDefinitionId": 60042,
  "ParentId": 60041,
  "ParentDottedKey": "Dynamic.ThesaurusTest",
  "Family": "Dynamic",
  "Translations": {
    "en_US": "Label EN",
    "fr_BE": "Label FR",
    "nl_BE": "Label NL",
    "en": "Label EN",
    "fr": "Label FR",
    "nl": "Label NL"
  },
  "Type": "ThesaurusLabelField",
  "Searchable": true,
  "ReadOnly": false,
  "Required": false,
  "GlobalSearch": false,
  "AdvancedSearch": false,
  "Sortable": false,
  "Inheritance": "None",
  "LongTranslations": {
    "en_US": "Thesaurus Test > Label EN",
    "fr_BE": "Thesaurus Test > Label FR",
    "nl_BE": "Thesaurus Test > Label NL",
    "en": "Thesaurus Test > Label EN",
    "fr": "Thesaurus Test > Label FR",
    "nl": "Thesaurus Test > Label NL"
  },
  "IndexName": "indexName",
  "Lang": "nl"
}
```

#### EnumField properties {#field_definition_enum_properties}

Properties only applicable for type `EnumField`:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| PossibleValues | String[] | `Deprecated property, might be removed in the future. Values is used instead` List of values for type EnumField. | yes |  |  |
| Values | Map[] | List of values for type EnumField. |  |  | yes |
| Values.Value > Label | String | The label for the enum value. |  |  | yes |
| Values > Active | Boolean | Whether the enum value is active. When editing the metadata of a record, this field can no longer be changed to a value which is not active. |  | true |  |
| Values > ChangeType | Enum(`Delete`,`Create`, `Update`) | When in draft mode this field displays the type of change | yes |  |  |
| Values > Status | Enum(`Draft`,`Processing`, `Published`) | When the field is `Processing` it’s no longer editable. Only `Published` options are usable for ingestion | yes |  |  |
| Values > Version | Number | The version of this field value | yes |  |  |
| Values > Initiator | Enum(`System`,`Migration`, `User`) | Who initiated the change to a field value. User changes are always `User` | yes |  |

```json
{
  "Key": "ImageQuality",
  "FlatKey": "ImageQuality",
  "DottedKey": "Technical.ImageQuality",
  "FieldDefinitionId": 208,
  "ParentId": null,
  "Family": "Technical",
  "Translations": {
    "en_US": "Image quality",
    "fr_BE": "Qualité de l'image",
    "nl_BE": "Beeldkwaliteit",
    "en": "Image quality",
    "fr": "Qualité de l'image",
    "nl": "Beeldkwaliteit"
  },
  "Type": "EnumField",
  "Searchable": true,
  "ReadOnly": true,
  "Required": false,
  "GlobalSearch": true,
  "AdvancedSearch": true,
  "Sortable": true,
  "Inheritance": "None",
  "LongTranslations": {
    "en_US": "Image quality",
    "fr_BE": "Qualité de l'image",
    "nl_BE": "Beeldkwaliteit",
    "en": "Image quality",
    "fr": "Qualité de l'image",
    "nl": "Beeldkwaliteit"
  },
  "PossibleValues": [
    "high",
    "medium",
    "low"
  ],
  "Values" : [
    {
      "Value" : {
        "Label": "high" 
      },
      "Active": true
    },
    {
      "Value" : {
        "Label": "medium"
      },
      "Active": true
    },
    {
      "Value": {
        "Label": "low"
      },
      "Active": true
    }
  ],
  "IndexName": "indexName"
}
```

#### VectorField properties {#field_definition_vector_properties}

Properties only applicable for fields with (main) type `VectorField`:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Dimensions | Integer | The number of dimensions of the vector. Must be in the interval [1,10000]. | yes, after creation | 1 | yes |

#### ListField properties {#field_definition_list_properties}

Properties only applicable for fields with (main) type `ListField`:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| SubKey | String | The key of the sub field | yes, after creation |  |  |
| SubType | String | The type of the sub field | yes, after creation | SimpleField |

When providing the `SubKey` the subfield will automatically be created

#### ComplexListField properties {#field_definition_complex_list_properties}

Properties only applicable for fields with (main) type `ComplexListField`:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| SubKey | String | The key of the sub field | yes, after creation |  |  |
| SubType | String | The type of the sub field | yes, after creation | SimpleField |

When providing the `SubKey` the subfield will automatically be created

#### SimpleField properties {#field_definition_simple_properties}

Properties only applicable for fields with (main) type `SimpleField`:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Regex | String | Regular expression used to validate the value of the field when saving a record. | yes, after creation |  |

> Note: Empty values are always considered valid regardless of the regular expression.

```json
{
  "Key": "Title",
  "FlatKey": "Title",
  "DottedKey": "Descriptive.Title",
  "FieldDefinitionId": 1,
  "ParentId": null,
  "ParentDottedKey": "",
  "Family": "Descriptive",
  "Translations": {
    "en_US": "Title",
    "fr_BE": "Titre",
    "nl_BE": "Titel",
    "en": "Title",
    "fr": "Titre",
    "nl": "Titel"
  },
  "Type": "SimpleField",
  "Searchable": true,
  "ReadOnly": false,
  "Required": true,
  "GlobalSearch": true,
  "AdvancedSearch": true,
  "Sortable": true,
  "Inheritance": "Propagation",
  "LongTranslations": {
    "en_US": "Title",
    "fr_BE": "Titre",
    "nl_BE": "Titel",
    "en": "Title",
    "fr": "Titre",
    "nl": "Titel"
  },
  "IndexName": "indexName",
  "Regex": "^[A-Za-z0-9]+$",
  "Context": {
    "IsEditable": false,
    "IsDeletable": false,
    "HasEditableChildren": false
  }
}
```

### Flat field definition object structure {#field_definition_flat_object}

Properties of [Field definition](#field_definition_object) object, extended with following properties:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| ChildrenFlat | Array of ChildrenFlat Objects. |  | yes |  |  |
| ChildrenFlat.FieldDefinitionId | `Deprecated property, might be removed in the future.` Number | The Id of the child field definition. | yes |  |  |
| ChildrenFlat.FlatKey | String | The FlatKey of the child field definition. | yes |  |  |
| ChildrenFlat.DottedKey | String | The DottedKey of the child field definition. | yes |  |

```json
{
  "Key": "ThesaurusTest",
  "FlatKey": "ThesaurusTest",
  "DottedKey": "Dynamic.ThesaurusTest",
  "FieldDefinitionId": 60041,
  "ParentId": null,
  "Family": "Dynamic",
  "Translations": {
    "en_US": "Thesaurus Test",
    "fr_BE": "ThesaurusTest",
    "nl_BE": "ThesaurusTest",
    "en": "Thesaurus Test",
    "fr": "ThesaurusTest",
    "nl": "ThesaurusTest"
  },
  "Type": "ThesaurusField",
  "Searchable": true,
  "ReadOnly": false,
  "Required": false,
  "GlobalSearch": false,
  "AdvancedSearch": false,
  "Sortable": false,
  "Inheritance": "None",
  "LongTranslations": {
    "en_US": "Thesaurus Test",
    "fr_BE": "ThesaurusTest",
    "nl_BE": "ThesaurusTest",
    "en": "Thesaurus Test",
    "fr": "ThesaurusTest",
    "nl": "ThesaurusTest"
  },
  "Scheme": {
    "Id": "784a2b17-ac28-495f-93f5-8647181ac059",
    "ExternalThesaurusId": "3f148ec0-2a24-4e33-97d8-7d80537be071",
    "Name": "Collection hobbies",
    "TopConcept": "https://dev.mediahaven.com/thesaurus/_f6765036",
    "MinNarrower": 1,
    "MaxNarrower": 1
  },
  "IndexName": "indexName",
  "ChildrenFlat": [
    {
      "FlatKey": "ThesaurusTestUri",
      "FieldDefinitionId": 60042,
      "DottedKey": "Dynamic.ThesaurusTest.Uri"
    }
  ]
}
```

### Nested field definition object structure {#field_definition_nested_object}

Properties of [Field definition](#field_definition_object) object, extended with following properties:

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Children | Array of [Nested field definition](#field_definition_nested_properties) objects. |  |  |  |

```json
{
  "Key": "ThesaurusTest",
  "FlatKey": "ThesaurusTest",
  "DottedKey": "Dynamic.ThesaurusTest",
  "FieldDefinitionId": 60041,
  "ParentId": null,
  "Family": "Dynamic",
  "Translations": {
    "en_US": "Thesaurus Test",
    "fr_BE": "ThesaurusTest",
    "nl_BE": "ThesaurusTest",
    "en": "Thesaurus Test",
    "fr": "ThesaurusTest",
    "nl": "ThesaurusTest"
  },
  "Type": "ThesaurusField",
  "Searchable": true,
  "ReadOnly": false,
  "Required": false,
  "GlobalSearch": false,
  "AdvancedSearch": false,
  "Sortable": false,
  "Inheritance": "None",
  "LongTranslations": {
    "en_US": "Thesaurus Test",
    "fr_BE": "ThesaurusTest",
    "nl_BE": "ThesaurusTest",
    "en": "Thesaurus Test",
    "fr": "ThesaurusTest",
    "nl": "ThesaurusTest"
  },
  "Scheme": {
    "Id": "784a2b17-ac28-495f-93f5-8647181ac059",
    "ExternalThesaurusId": "3f148ec0-2a24-4e33-97d8-7d80537be071",
    "Name": "Collection hobbies",
    "TopConcept": "https://dev.mediahaven.com/thesaurus/_f6765036",
    "MinNarrower": 1,
    "MaxNarrower": 1
  },
  "IndexName": "indexName",
  "Children": [
    {
      "Key": "Uri",
      "FlatKey": "ThesaurusTestUri",
      "DottedKey": "Dynamic.ThesaurusTest.Uri",
      "FieldDefinitionId": 60042,
      "ParentId": 60041,
      "Family": "Dynamic",
      "Translations": {
        "en_US": "Uri",
        "fr_BE": "Uri",
        "nl_BE": "Uri",
        "en": "Uri",
        "fr": "Uri",
        "nl": "Uri"
      },
      "Type": "ThesaurusUriField",
      "Searchable": true,
      "ReadOnly": false,
      "Required": false,
      "GlobalSearch": false,
      "AdvancedSearch": false,
      "Sortable": false,
      "Inheritance": "None",
      "LongTranslations": {
        "en_US": "Thesaurus Test > Uri",
        "fr_BE": "ThesaurusTest > Uri",
        "nl_BE": "ThesaurusTest > Uri",
        "en": "Thesaurus Test > Uri",
        "fr": "ThesaurusTest > Uri",
        "nl": "ThesaurusTest > Uri"
      },
      "Children": []
    }
  ]
}
```

### Retrieve the options of an Enum Map Field {#field_definitions_options}

Retrieve a list of [Field Definition Option](#field_definition_option) using a `GET` request

The options of an Enum Map Field are only available as a sub-endpoint of the field definition.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey/values
```

> Note: Requesting the values of a field definition by `fieldDefinitionId` or `flatKey` is deprecated, use `dottedKey` instead.

You can query all subfields of this field by sending get-parameters for those fields. Subfield query’s support the ‘\*’
wildcard. For example, when searching for “Reception” you can use following wildcards:

- Recep\*
- Rec\*ion

The default fields available are:

- OrganisationId: To find all options defined for this organisation (and also the global defined options). By default set to null if the user has the function ADMIN_VIEW_ALL_ORGANISATIONS: null, otherwise the organisation of the user.
- Label: The label

The options are listed in the following order:
- non-specific organisation options, sorted by label in alphabetical order
- specific organisation options, sorted by organisation id
- specific organisation options, sorted by their order number (if present)
- specific organisation options, sorted by label in alphabetical order if no order number is present

Additionally, the following query parameters can be used:

| Query parameter | Type | Description | Default | required |
| --- | --- | --- | --- | --- |
| mode | Enum(`Production`, `Draft`) | If you want to edit values you need to be in `Draft` mode | `Production` | no |
| onlyActive | Boolean | If true, only active values are returned, otherwise all values are returned | true | no |

#### Response

- `200` List of [FieldDefinitionOption](#field_definition_option)
- `400` The field is not of the type EnumMapField
- `403` User has no access to the organisation
- `404` Field does not exist

### Retrieve a single option of an Enum Map Field {#field_definitions_options_get}

Retrieve a single [Field Definition Option](#field_definition_option) using a `GET` request

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey/values/:id
```

> Note: Requesting a single option of a field definition by `fieldDefinitionId` is deprecated, use `dottedKey` instead.

#### Response

- `200` [FieldDefinitionOption](#field_definition_option)
- `400` The field is not of the type EnumMapField
- `404` Field or option does not exist

### List the possible concepts of a ThesaurusField {#field_definitions_concepts}

Retrieve a list of possible concepts [Thesaurus concept](#thesaurus_concept) using a `GET` request

This endpoint is only available on a ThesaurusField.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey/concepts
```

> Note: Requesting the concepts of a field definition by `fieldDefinitionId` is deprecated, use `dottedKey` instead.

The results are limited to the concept configured on the field definition. The standard [Page parameters](#page-filter)
are available on this endpoint.

| Query parameter | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| q | String | The string you wish to match |  | yes |
| lang | String | The language in you wish to search in. Format: ISO 639-1 (eg, nl for dutch) | All languages | no |
| nrOfResults | Number | The number of results that will be returned up to a maximum of 100 | 25 | no |
| startIndex | Number | The start index of the search | 0 | no |
| sortLang | String | The results will be sorted based on the preferred label of this language. Format: ISO 639-1 (eg, nl for dutch) | user language | no |

> Note: When searching for concepts not only the preferred labels but also the alternative labels are matched. This means a concept might not match on the preferred label but could match on an alternative label.
> Note: Requesting the concepts of a ThesaurusField by `flatKey` is deprecated, use `dottedKey` instead.

#### Response

- `200` A [Page](#page) of [Thesaurus concept](#thesaurus_concept)
- `404` Field does not exist
- `400` The field is not of the type ThesaurusField

### Get the detail of a concept of a ThesaurusField {#field_definitions_concept_detail}

Get the details of a concept [Thesaurus concept](#thesaurus_concept) using a `GET` request

This endpoint is only available on a ThesaurusField.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey/concepts/:thesaurusId
```

Returns a [Thesaurus concept](#thesaurus_concept)

The `thesaurusId` field is only the last part of the uri ( <https://archief.viaa.be/mediahaven-rest-api/thesaurus/> `:thesaurusId` ). The
results are limited to the concept configured on the field definition.

> Note: Requesting the details of a concept of a ThesaurusField by `fieldDefinitionId` or `flatKey` is deprecated, use `dottedKey` instead.

#### Response

- `200` A [Thesaurus concept](#thesaurus_concept)
- `404` Field or concept does not exist
- `400` The field is not of the type ThesaurusField

### List the details of the narrower concepts of a specific concept {#field_definitions_concepts_narrower}

Retrieve a list of narrower concepts [Thesaurus concept](#thesaurus_concept) using a `GET` request

This endpoint is only available on a ThesaurusField.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey/concepts/:thesaurusId/narrower
```

The results are limited to the concept configured on the field definition.
The standard [Page parameters](#page-filter) are available on this endpoint.

> Note: Requesting the narrower concepts of a concept of a ThesaurusField by `fieldDefinitionId` or `flatKey` is deprecated, use `dottedKey` instead.

| Query parameter | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| sortLang | String | The results will be sorted based on the preferred label of this language. Format: ISO 639-1 (eg, nl for dutch) | user language | no |
| nrOfResults | Number | The number of results that will be returned up to a maximum of 100 | 25 | no |
| startIndex | Number | The start index of the search | 0 | no |

#### Response

- `200` A [Page](#page) of [Thesaurus concept](#thesaurus_concept)
- `404` Field or concept does not exist
- `400` The field is not of the type ThesaurusField

### Create option of an Enum Map Field {#create_field_definitions_options}

Create an option using a `POST` request containing a [Field Definition Option](#field_definition_option):

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey/values
```

> Note: Create options for a field definition using `field-definitions` or `flatKey` is deprecated, use `dottedKey` instead.
>
> The changes will be automatically published if the given field definition is also in `Published` mode.
> Otherwise, the changes are only visible in `Draft` mode. To publish the change call the [publish action](#publish_field_changes_action)

#### Response

- `202` Created [Field Definition Option](#field_definition_option)
- `400` The field is not of the type EnumMapField or one or more of the provided property values were not valid
- `403` User does not have the correct function
- `404` Field does not exist
- `409` The label already exists

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_FIELD_DEFINITIONS’ function.
- Creating options for a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Update option of an Enum Map Field {#field_definitions_options_patch}

A single option can be updated by performing a `PUT`-request containing a [Field Definition Option](#field_definition_option):

```http
https://archief.viaa.be/mediahaven-rest-api/v2/field-definitions/:dottedKey/values/:id
```

> The changes will be automatically published if the given field definition is also in `Published` mode.
> After publishing, a batch will be started to update the records that contain the modified option (only if child field definition with key `Id` is searchable).
> Otherwise, the changes are only visible in `Draft` mode. To publish the change call the [publish action](#publish_field_changes_action)

#### Response

- `200` Updated [FieldDefinitionOption](#field_definition_option)
- `400` The field is not of the type EnumMapField or one or more of the provided property values were not valid
- `403` User does not have the correct function
- `404` Field or option does not exist
- `409` The label already exists

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_FIELD_DEFINITIONS’ function.
- Updating options for a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Field definition option object {#field_definition_option}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Value.Id | String | Identifier of option. | yes |  |  |
| Value.Label | String | the label of the option. |  |  | yes |
| Value.SubKey | String | Value of an optional subkey |  |  |  |
| OrganisationId | Number | The organisation this option belongs to. | yes, after creation |  | yes |
| Active | Boolean | Whether the option can be used. |  | yes |  |
| ChangeType | Enum(`Delete`,`Create`, `Update`) | When in draft mode this field displays the type of change. | yes |  |  |
| Status | Enum(`Draft`,`Processing`, `Published`) | When the field is `Processing` it’s no longer editable. Only `Published` options are usable for ingestion. | yes |  |  |
| Version | Number | The version of this field. | yes |  |  |
| Initiator | Enum(`System`,`Migration`, `User`) | Who initiated the change to a field. User changes are always `User`. | yes |  |  |
| Order | Double | A sequence number used for sorting a list of options. Only applicable for organisation specific options. |  | current max order number + 1 |  |
| Context.IsEditable | Boolean | Whether the option is editable. | yes |  |  |
| Context.CanApplyOrder | Boolean | Whether the order property can be set. | yes |  |

> Note: An order number is not required to be unique, so the same order number may appear multiple times.

```json
{
  "Active": true,
  "OrganisationId": 100,
  "Value": {
    "Id": "18",
    "Label": "Review of the new samsung galaxy tab",
    "SubKey": ""
  },
  "Status" : "Published",
  "Version": 1,
  "Initiator": "User",
  "Context": {
    "IsEditable": "true",
    "CanApplyOrder": "true"
  },
  "Order": 2.0
}
```

### Thesaurus concept {#thesaurus_concept}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Uri | String | The uri/unique identifier of concept. |  | yes |
| PreferredLabels | Label[] | The preferred labels of the thesaurus | empty list | no |
| PreferredLabels.Lang | String | Language |  | no |
| PreferredLabels.Label | String | Label |  | no |
| Breadcrumbs | Label[] | Breadcrumbs starting from the top concept to the actual concept | empty list | no |
| Breadcrumbs.Lang | String | The language of the breadcrumb trail |  | no |
| Breadcrumbs.Label | String | Breadcrumb trail from the preferred label of the top concept to this child | empty list | no |
| AlternativeLabels | Label[] | The alternative labels of the thesaurus | empty list | no |
| AlternativeLabels.Lang | String | Language |  | no |
| AlternativeLabels.Label | String | Label |  | no |
| Broader | String[] | Uri of parent concept (multiple possible if linked to several parents). | empty list | no |
| BroaderTransitive | String[] | Uri of all broader concepts (parents inherited from parent). Ordered from the grandparent to the root defined in the field definition. | empty list | no |
| Narrower | String[] | Uri of child concept. | empty list | no |
| Selectable | Boolean | Check if the item is selectable |  | no |

```json
{
  "Uri": "https://dev.mediahaven.com/thesaurus/ID1656",
  "PreferredLabels": [
    {
      "Lang": "nl",
      "Label": "Museum voor moderne kunst Luik"
    },
    {
      "Lang": "en",
      "Label": "Musée d'art moderne"
    },
    {
      "Lang": "fr",
      "Label": "Musée d'art moderne"
    },
    {
      "Lang": "de",
      "Label": "Musée d'art moderne"
    }
  ],
  "Breadcrumbs": [
    {
      "Lang": "nl",
      "Label": "Cultuur > Musea > Museum voor moderne kunst Luik"
    }
  ],
  "AlternativeLabels": [],
  "Broader": ["https://dev.mediahaven.com/thesaurus/ID1652"],
  "BroaderTransitive": [
    "https://dev.mediahaven.com/thesaurus/ID1238",
    "https://dev.mediahaven.com/thesaurus/ID970"
  ],
  "Narrower": [],
  "Selectable": true
}
```

### Field definition action object {#field_definition_action}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Action | Enum (`PublishDrafts`, `ResetDrafts`) | The type of action |  | yes |
| IndexName | String | The index name to apply the action on | If user has the function ADMIN_EDIT_ALL_ORGANISATIONS: null, otherwise the index name of the organisation of the current user |  |
| Initiator | Enum (`Migration`,`System`,`User`) | The type of migration to apply | `User` |  |
| AllowedSubactions | Enum[] (`PublishDirectly`,`PublishAfterRefresh`,`PublishAfterReindex`,`PublishAfterRebuild`) | The allowed subactions that may be executed. Only applicable for Action = `PublishDrafts`. | [`PublishDirectly`,`PublishAfterRefresh`] |

Notes:
- Only users with the function `ADMIN_BACKEND_SERVICES` are allowed to change the `Initiator` property and use the action `ResetDrafts`.
- See [Field definition action result](#field_definition_action_result) for a description of the possible subactions

Example:

```json
{
  "Action": "PublishDrafts",
  "IndexName": "indexName",
  "Initiator": "User",
  "AllowedSubactions": ["PublishDirectly", "PublishAfterRefresh"]
}
```

### Field definition action result object {#field_definition_action_result}

| Property | Type | Description |
| --- | --- | --- |
| Subaction | Enum (`PublishDirectly`, `PublishAfterRefresh`, `PublishAfterReindex`, `ResetPendingChanges`) | The subaction that is performed under the hood as a result of the initiated Action |

Following subactions belong to the action `PublishDrafts`:
- `PublishDirectly`: field definitions can be directly published, no refresh or reindex in SOLR needed
- `PublishAfterRefresh`: field definitions can be published after a refresh in SOLR, no reindex needed
- `PublishAfterReindex`: field definitions can be published after a refresh and reindex in SOLR

Following subactions belong to the action `ResetDrafts`:
- `ResetPendingChanges`: field definitions with status `Processing` are reset to status `Draft`.

Example:

```json
{
  "Subaction": "PublishAfterRefresh"
}
```

## Thesauri {#thesauri}

A thesaurus is a hierarchical structure where translations and synonyms can be provided for each
concept forming a part of the structure. Under a thesaurus multiple [schemes](#thesaurus_schemes) can be defined
and linked with a [thesaurus field definition](#field_definition_thesaurus_properties).
New concepts for the thesaurus can be proposed using [thesaurus suggestions](#thesaurus-suggestions).

Additional information can be
found [here](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2903638026/21.2+-+Thesaurus).

### Required functions {#thesauri_functions}

- Reading thesauri from the organisation of the user requires no functions
- Reading thesauri from other organisations requires the function `ADMIN_VIEW_ALL_ORGANISATIONS`
- Modifying thesauri from the organisation of the user requires the function `ADMIN_THESAURI`
- Modifying thesauri from other organisations additionally requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`

### Thesaurus object structure {#thesauri_model}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Id | String (UUID) | A unique thesaurus ID. | Yes |  | No |
| Name | String | Unique name of the thesaurus across all organisations. Starting the name of the thesaurus with the organisation name is recommended. | No | Empty | Yes |
| OrganisationId | Number | The ID of the organisation the thesaurus belongs to. | Yes once created. | Organisation of the user | No |
| ExternalId | String | Unique identifier of the thesaurus in underlying service atramhasis. | Yes | Automatically created | No |
| LastUpdatedInIndex | Date (ISO8601) | The date when the changes in the thesauri were exported to the index. | Yes |  | No |
| CreationDate | Date (ISO8601) | The date when the thesaurus was created. | Yes |  | No |
| LastModifiedDate | Date (ISO8601) | The date when the thesaurus was last modified. | Yes |  | No |

Example:

```json
{
  "Id": "60aca242-97ff-47d6-97d5-0430a0882042",
  "Name": "My thesaurus",
  "OrganisationId": 100,
  "ExternalId": "12",
  "LastUpdatedInIndex": "2022-10-16T18:25:29.000000Z",
  "LastModifiedDate": "2022-10-18T14:20:21.193000Z",
  "CreationDate": "2022-10-16T14:20:11.000000Z"
}
```

### Getting a specific thesaurus {#thesauri_get}

Getting a specific thesaurus is done by sending a GET-request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:id
```

#### Response

- `200` Ok. [thesaurus](#thesauri_model)
- `403` If the user does not have the required functions to call this method.
- `404` If the thesaurus doesn’t exist.

### Listing all thesauri {#thesauri_get_all}

A list of all thesauri can be retrieved using a `GET` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Organisation to search in. Requires function `ADMIN_VIEW_ALL_ORGANISATIONS` if searching in other organisations. | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| name | Name of the thesaurus |  |
| id | ID of thesaurus |  |
| externalId | External ID of thesaurus |  |
| sort | Sort on one of the following fields (Name, Id, LastUpdatedInIndex, CreationDate, LastModifiedDate) | Name |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

#### Response

- `200` Ok. [Page](#page) of [thesauri](#thesauri_model)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

### Create thesaurus {#thesauri_create}

To create a new thesaurus you can send a `POST` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/
```

The endpoint supports JSON with the following properties:

### Create thesaurus object structure {#thesauri_model_create}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Name | String | Unique name of the thesaurus within the organisation | Empty | Yes |
| OrganisationId | Number | Organisation of the thesaurus. If different from the organisation of the user, it requires the function `ADMIN_EDIT_ALL_ORGANISATIONS` |  | No |

Example request body:

```json
{
  "Name": "My thesaurus",
  "OrganisationId": 109
}
```

#### Response

- `201` [created thesaurus](#thesauri_model)
- `400` One or more of the provided parameters are not valid
- `403` If the user does not have the required functions to call this method.
- `404` The provided organisation does not exist
- `409` A thesaurus with this name already exists

### Updating a thesaurus {#thesauri_edit}

Updating a thesaurus can be done by performing a `PUT` request with a [thesaurus](#thesauri_model) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:id
```

#### Response

- `200` [updated thesaurus](#thesauri_model)
- `403` If the user does not have the required functions to call this method.
- `404` If the thesaurus doesn’t exist.

### Deleting a thesaurus {#thesauri_delete}

Deleting a thesaurus is done by simple sending a `DELETE` request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:id
```

A thesaurus can only be deleted if none of its [schemes](#thesaurus_schemes) are linked with
a [thesaurus field definition](#field_definition_thesaurus_properties).

#### Response

- `204` If the thesaurus was deleted successfully.
- `403` If the user does not have the required functions to call this method.
- `404` If the thesaurus doesn’t exist.
- `409` If the thesaurus can’t be deleted because at least one of its [schemes](#thesaurus_schemes) is still linked with
  a thesaurus field definition

## Thesaurus schemes {#thesaurus_schemes}

A thesaurus scheme is a subtree in the hierarchical structure of the [thesaurus](#thesauri) to which it belongs.
A thesaurus scheme can be linked with a field definition for
[thesaurus field definitions](#field_definition_thesaurus_properties).
New concepts for the thesaurus can be proposed using [thesaurus suggestions](#thesaurus-suggestions).

Additional information can be
found [here](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/2903638026/21.2+-+Thesaurus).

### Required functions {#thesaurus_schemes_functions}

- Reading schemes requires read access to its [thesaurus](#thesauri_functions)
- Modifying schemes requires write access to its [thesaurus](#thesauri_functions)

### Thesaurus scheme object structure {#thesaurus_schemes_model}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Id | String (UUID) | A unique ID of the scheme. | Yes |  | No |
| ThesaurusId | String (UUID) | A unique ID of the thesaurus to which it belongs. | Yes once created |  | No |
| OrganisationId | Number | A unique ID of the organisation of the thesaurus scheme. Inherited from the thesaurus. | Yes | Inherited from thesaurus | No |
| Name | String | Unique name of the scheme within the thesaurus. | No | Empty | Yes |
| TopConcept | String | URI of the concept forming the root of the subtree within the thesaurus. | No | Root concept of thesaurus | No |
| MaxBroader | Number | How much higher in the tree ancestors are picked for enrichment. For example in a thesaurus about mammals, the broader concept label “Vertebrate” is also enriched when indexing. | No | 0 | No |
| MinNarrower | Number | Only concepts starting from this depth relative to the top concept can be assigned as metadata. e.g. in an animal thesaurus you cannot assign the concept “mammal”, but you can assign the concept “lion” (a narrower concept) | No | 1 | No |
| MaxNarrower | Number | Only concepts up to this depth relative to the top concept can be assigned as metadata. e.g. in an animal thesaurus you can assign the concept “lion”, but you cannot assign the concept “transvaal lion” (a narrower concept) | No | 99 | No |
| CreationDate | Date (ISO8601) | The date when the scheme was created. | Yes | Now | No |
| LastModifiedDate | Date (ISO8601) | The date when the scheme last modified. | Yes | Now | No |

Example:

```json
{
  "Id": "60aca242-97ff-47d6-97d5-0430a0882042",
  "ThesaurusId": "b40780dd-39f9-4b04-ab49-865f350a3b95",
  "Name": "My thesaurus scheme",
  "OrganisationId": 100,
  "LastModifiedDate": "2022-10-18T14:20:21.193000Z",
  "CreationDate": "2022-10-16T14:20:11.000000Z",
  "TopConcept": "https://integration.mediahaven.com/thesaurus/conceptschemes/animals/c/1",
  "MaxBroader": 0,
  "MinNarrower": 1,
  "MaxNarrower": 99
}
```

### Getting a specific scheme for a thesaurus {#thesaurus_schemes_get}

Getting a specific thesaurus scheme is done by sending a GET-request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:thesaurusId/schemes/:id
```

#### Response

- `200` Ok. [scheme](#thesaurus_schemes_model)
- `403` If the user does not have the required functions to call this method.
- `404` If the thesaurus scheme doesn’t exist within this thesaurus

### Listing all schemes of a thesaurus {#thesaurus_schemes_get_all}

A list of all schemes within a thesaurus can be retrieved using a `GET` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:thesaurusId/schemes/
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| name | Name of the scheme |  |
| id | ID of the scheme |  |
| topConcept | URI of the top concept |  |
| sort | Sort on one of the following fields (Name, Id, CreationDate, LastModifiedDate, TopConcept) | Name |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

#### Response

- `200` Ok. [Page](#page) of [schemes](#thesaurus_schemes_model)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

### Create a thesaurus scheme {#thesaurus_schemes_create}

To create a new scheme you can send a `POST` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:thesaurusId/schemes
```

The endpoint supports JSON with the following properties:

### Create thesaurus scheme object structure {#thesaurus_schemes_model_create}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Name | String | Unique name of the thesaurus within the organisation | Empty | Yes |
| TopConcept | String | URI of the concept forming the root of the subtree within the thesaurus. | Empty | Yes |
| MaxBroader | Number | How much higher in the tree ancestors are picked for enrichment. For example in a thesaurus about mammals, the broader concept label “Vertebrate” is also enriched when indexing. | 0 | No |
| MinNarrower | Number | Only concepts starting from this depth relative to the top concept can be assigned as metadata. e.g. In an animal thesaurus you cannot assign the concept “mammal”, but you can assign the concept “lion” (a narrower concept) | 1 | No |
| MaxNarrower | Number | Only concepts up to this depth relative to the top concept can be assigned as metadata. e.g. In an animal thesaurus you can assign the concept “lion”, but you cannot assign the concept “transvaal lion” (a narrower concept) | 99 | No |

Extra rules:

- `TopConcept` exists as concept within the thesaurus
- `MinNarrower`, `MaxNarrower`, `MaxBroader` `>= 0`
- `MinNarrower <= MaxNarrower`

Example request body:

```json
{
  "Name": "My thesaurus",
  "TopConcept": "https://integration.mediahaven.com/thesaurus/conceptschemes/animals/c/1",
  "MinNarrower": 2,
  "MaxNarrower": 5
}
```

#### Response

- `200` [created scheme](#thesaurus_schemes_model)
- `400` One or more of the provided parameters are not valid
- `403` If the user does not have the required functions to call this method.
- `404` The provided organisation does not exist
- `409` A scheme with this name already exists within the thesaurus

### Updating a thesaurus scheme {#thesaurus_schemes_edit}

Updating a thesaurus can be done by performing a `PUT` request with a [thesaurus](#thesaurus_schemes_model) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:thesaurusId/schemes/:id
```

#### Response

- `200` [updated scheme](#thesaurus_schemes_model)
- `403` If the user does not have the required functions to call this method.
- `404` If the scheme does not exist within the thesaurus

### Deleting a thesaurus scheme {#thesaurus_schemes_delete}

Deleting a thesaurus is done by simple sending a `DELETE` request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/thesauri/:thesaurusId/schemes/:id
```

A thesaurus scheme can only be deleted if it is no longer linked with
a [thesaurus field definition](#field_definition_thesaurus_properties).

#### Response

- `204` If the scheme was deleted successfully.
- `403` If the user does not have the required functions to call this method.
- `404` If the schemes does not exist within the thesaurus
- `409` If the scheme can’t be deleted because it is still linked with
  a [thesaurus field definition](#field_definition_thesaurus_properties)

## Thesaurus Suggestions {#thesaurus-suggestions}

Thesaurus suggestions allow for users to suggest new terms for a thesaurus. The suggestion is created for a particular
thesaurus field definition and list of records. The suggestion is afterwards evaluated by another user which can take
the following decisions:

- Accept: The suggestion is added to the thesaurus and applied to all linked records
- Reject: TBC in next sprint
- Transform: TBC in next sprint

### Required functions {#mediahaven-rest-api-manual-thesaurus-suggestions-required-functions}

- `THESAURUS_SUGGESTIONS_SUBMIT`: Submit new suggestions
- `THESAURUS_SUGGESTIONS_EVALUATE`: Evaluate suggestions

### Properties {#mediahaven-rest-api-manual-thesaurus-suggestions-properties}

Suggestions have the following noteworthy properties

| Metadata Field | Description |
| --- | --- |
| `Structural.FieldDefinition` | Describes the field definition for the suggestion is made |
| `Structural.Relations.IsSuggestedFor` | List of records on which to apply the suggestion |
| `Descriptive.Title` | The label of the suggestion |
| `Descriptive.UploadedBy` | The name of the user which created the suggestion |
| `Internal.RecordId` | The unique ID of the suggestion |
| `Administrative.RecordStatus` | The status of the suggestion: `Submitted`, `Processing`, `Rejected`, `Published` |
| `Administrative.RecordType` | `ThesaurusSuggestion` |
| `RecordInformation.PreferredLabels` | The preferred labels of the suggestion |  |
| `RecordInformation.AlternativeLabels` | The alternative labels of the suggestion |

The equivalent `application/json` is

```json
{
    "Structural": {
        "FieldDefinition": {
            "LongTranslations": {
                "En": "Categories",
                "Fr": "Catégories",
                "Nl": "Categorieën"
            },
            "DottedKey": "Descriptive.LimitedCategories.Category"
        },
        "Relations": {
            "IsSuggestedFor": [
                "FragmentId-1",
                "FragmentId-2"
            ]
        }
    },
    "Descriptive": {
        "Title": "Guinea Pig",
        "UploadedBy": "John Doe",
        "CreationDate": "2021-05-21T08:14:23.000000Z"
    },
    "Internal": {
        "RecordId": "2ae64fa5dc6147239f8956ed4049eb7cfd55a00695f24136b2ee826a99c3419a"
    },
    "Administrative": {
        "OrganisationName": "mh-dev",
        "RecordStatus": "Submitted",
        "RecordType": "ThesaurusSuggestion"
    },
    "Context": {
        "IsEditable": true,
        "IsDeletable": true,
        "IsPublic": false,
        "IsExportable": true,
        "Profiles": []
    },
    "RecordInformation" : {
        "PreferredLabels" : {
          "PreferredLabel" : [
            {
              "Lang": "nl",
              "Label": "cavia"
            },
            {
              "Lang": "en",
              "Label": "Guinea Pig"
            }
          ]
        },
        "AlternativeLabels" : {
          "AlternativeLabel" : [
            {
              "Lang": "en",
              "Label": "cavy"
            },
            {
              "Lang": "en",
              "Label": "domestic cavy"
            }
          ]
        }
    }
}
```

### Model {#mediahaven-rest-api-manual-thesaurus-suggestions-model}

Suggestions are specialised records and hence an extension on the existing endpoints for

- [search on records](#search-for-media-objects)
- [delete records](#delete)

The returned objects are [Records](#record-object).

### Submitting {#thesaurus-suggestions-functions}

Create a new suggestion by doing a `POST`

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/thesaurus-suggestions
```

with as body of content type `application/json` with properties

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Label | String | The default label of the suggestion to create. By default, this label will be assigned to each supported language and can be overwritten by the property PreferredLabels |  | yes |
| PreferredLabels | Label[] | The preferred labels of the suggestion to create. Only one unique label per language is allowed. |  | no |
| PreferredLabels.Lang | String | One of the supported languages of the thesaurus field definition |  | no |
| PreferredLabels.Label | String | Label |  | no |
| AlternativeLabels | Label[] | The alternative labels of the suggestion to create. Multiple labels per language are allowed. |  | no |
| AlternativeLabels.Lang | String | One of the supported languages of the thesaurus field definition |  | no |
| AlternativeLabels.Label | String | Label |  | no |
| DottedKey | String | The dotted key of a thesaurus field definition |  | yes |
| Records | String[] | List of record IDs for which to create the suggestion |  | no |

Requires the function `THESAURUS_SUGGESTIONS_SUBMIT`.

#### Example

```json
{
  "Label": "Guinea Pig",
  "PreferredLabels": [
    {
      "Lang": "nl",
      "Label": "cavia"
    },
    {
      "Lang": "en",
      "Label": "Guinea Pig"
    }
  ],
  "AlternativeLabels": [
    {
      "Lang": "en",
      "Label": "cavy"
    },
    {
      "Lang": "en",
      "Label": "domestic cavy"
    }
  ],
  "DottedKey": "Descriptive.LimitedCategories.Category",
  "Records": ["RecordId-1", "RecordId-2"]
}
```

##### Restrictions

- The field definition must exist and be a valid thesaurus field definition, otherwise —> Bad Request
- Default/preferred/alternative labels must not be blank, otherwise -> Bad Request
- The language for a preferred or alternative label must be supported by the thesaurus field definition, otherwise -> Bad Request
- Only one preferred label per language is allowed, otherwise -> Bad Request
- Alternative labels must not be duplicated
    - If the same label and language appears more than once in the alternative labels -> Bad Request
    - If the same label and language also appears in the preferred labels -> Bad Request
- If the default label already exists
    - As preferred label in any language in the thesaurus —> Conflict
    - As existing suggestion with status
        - Published, Processing —> Conflict
        - Submitted:
            - Append provided records to the existing suggestion
            - Overwrite preferred and alternative languages
            - Return that suggestion
            - —> Created
        - Rejected: Create new suggestion, this might be restricted in the future —> Created
- If a preferred label in a specific language already exists
    - As preferred label in the same language in the thesaurus —> Conflict

#### Response

- `201` Created: [Record](#record-object)
- `400` Bad request: [Error result](#error) See restrictions above
- `403` Forbidden: [Error result](#error)
- `409` Conflict: [Error result](#error) See restrictions above

### Searching {#thesaurus-suggestions-searching}

To list all suggestions, make a `GET` request using the same parameters as for [records](#basic-searching).

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/thesaurus-suggestions?q=Animals&startIndex=0&nrOfResults=5
```

The syntax of this endpoint is exactly the same as for [records](#basic-searching) but only records
having `RecordType:ThesaurusSuggestion` are returned.

#### Example for getting all suggestions for a particular field

Make a `GET` request with filter on the field `Structural.FieldDefinition.DottedKey` points to a particular thesaurus
field definition such as for example `Descriptive.LimitedCategories.Category`.

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/thesaurus-suggestions?q=%2b(Structural.FieldDefinition.DottedKey:Descriptive.LimitedCategories.Category)
```

### Getting a specific suggestion {#thesaurus-suggestions-get}

To get a specific suggestion, make a `GET` request using its `RecordId`

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/thesaurus-suggestions/:recordId
```

The syntax is exactly the same as for [records](#get_record) but it will raise
`400` Bad request when the record has a `RecordType` different from `ThesaurusSuggestion`.

### Deleting a suggestion {#thesaurus-suggestions-delete}

To remove a suggestion, make a `DELETE` request using its `RecordId`

```http
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/thesaurus-suggestions/:recordId
```

The syntax is exactly the same as for [records](#deleting) but it will raise
`400` Bad request when the record has a `RecordType` different from `ThesaurusSuggestion`.

Requires the functions `THESAURUS_SUGGESTIONS_SUBMIT` or `THESAURUS_SUGGESTIONS_EVALUATE`.

## User Suggestions {#user-suggestions}

With user suggestions you can suggest new users to be added to the system.

- Accept: The user is added
- Reject: The user is not added

### Required functions {#mediahaven-rest-api-manual-user-suggestions-required-functions}

- `USER_SUGGESTION_SUBMIT`: Submit new user
- `USER_SUGGESTION_EVALUATE`: Evaluate suggestions

### Properties {#mediahaven-rest-api-manual-user-suggestions-properties}

Suggestions have the following noteworthy properties

| Metadata Field | Description |
| --- | --- |
| `RecordInformation.UserContact.FirstName` | First name of the suggested user |
| `RecordInformation.UserContact.LastName` | Last name of the suggested user |
| `RecordInformation.UserContact.Email` | The email of the suggested user |
| `Descriptive.CreationDate` | The date the suggestion was added |
| `Internal.RecordId` | The unique ID of the suggestion |
| `Administrative.RecordStatus` | The status of the suggestion: `Submitted`, `Rejected`, `Published` |
| `Administrative.RecordType` | `UserSuggestion` |

The equivalent `application/json` is

```json
{
  "Descriptive": {
    "CreationDate": "2021-05-21T08:14:23.000000Z"
  },
  "Internal": {
    "RecordId": "2ae64fa5dc6147239f8956ed4049eb7cfd55a00695f24136b2ee826a99c3419a"
  },
  "Administrative": {
    "OrganisationName": "mh-dev",
    "RecordStatus": "Submitted",
    "RecordType": "UserSuggestion"
  },
  "RecordInformation": {
    "UserContact": {
      "FirstName": "Luke",
      "LastName": "Skywalker"
    }
  },
  "Context": {
    "IsEditable": true,
    "IsDeletable": true,
    "IsPublic": false,
    "IsExportable": true,
    "Profiles": []
  }
}
```

### Model {#mediahaven-rest-api-manual-user-suggestions-model}

Suggestions are specialised records and hence an extension on the existing endpoints for

- [search on records](#search-for-media-objects)
- [delete records](#delete)

The returned objects are [Records](#record-object).

### Submitting {#user-suggestions-functions}

Create a new suggestion by doing a `POST`

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/users/suggestions
```

with as body of content type `application/json` with properties

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| FirstName | String | First name of the user |  | yes |
| LastName | String | Last name of the user |  | yes |
| Email | String | The email of the user |  | yes |
| Password | String | The password of the user (plaintext) |  | yes |
| Locale | String | The locale of the user his language | Defaults to organisation default | no |

These are the default fields required for creation, additional fields can also be added, as defined in the child field
definitions for the `RecordInformation.UserContact` field.

**Note** the password is stored hashed and is not viewable or changeable after creation of the suggestion.

Requires the function `USER_SUGGESTION_SUBMIT`.

#### Example

```json
{
  "FirstName": "Luke",
  "LastName": "Skywalker",
  "Email": "starkiller@rebelalliance.com",
  "Password": "ItsATrap!",
  "Locale": "nl_BE"
}
```

#### Response

- `201` Created: [Record](#record-object)
- `400` Bad request: [Error result](#error)
- `403` Forbidden: [Error result](#error)
- `409` Conflict: [Error result](#error) A user already exists with this email

### Searching {#users-suggestions-searching}

To list all suggestions, make a `GET` request using the same parameters as for [records](#basic-searching).

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/users/suggestions?q=%2b(RecordInformation.UserContent.LastName:Skywalker)&startIndex=0&nrOfResults=5
```

The syntax of this endpoint is exactly the same as for [records](#basic-searching) but only records
having `RecordType:UserSuggestion` are returned.

### Getting a specific suggestion {#user-suggestions-get}

To get a specific suggestion, make a `GET` request using its `RecordId`

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/users/suggestions/:recordId
```

The syntax is exactly the same as for [records](#get_record) but it will raise
`400` Bad request when the record has a `RecordType` different from `UserSuggestion`.

### Deleting a suggestion {#user-suggestions-delete}

To remove a suggestion, make a `DELETE` request using its `RecordId`

```http
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/users/suggestions/:recordId
```

The syntax is exactly the same as for [records](#deleting) but it will raise
`400` Bad request when the record has a `RecordType` different from `UserSuggestion`.

Requires the functions `USER_SUGGESTIONS_SUBMIT` or `USER_SUGGESTIONS_EVALUATE`.

## User {#user-resource}

### Getting all users {#search_users}

Retrieve a [Page](#page) of [Users](#user_object) using a `GET` request:

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/users
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Organisation to search in | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| login | Login to search for |  |
| email | Email to search for |  |
| name | First or last name of user to search for |  |
| firstName | First name of user to search for |  |
| lastName | Last name of user to search for |  |
| userId | Id of user to search for |  |
| locale | Locale to search for |  |
| includeSystem | Whether to include users with authorization type different from Normal | false |
| sort | Sort on one of the following fields: Login, Email, FirstName, LastName, OrganisationId, Locale, CreationDate, LastModifiedDate | Login |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

> Note: you can use wildcards to filter on name, firstName, lastName, login and email.

#### Response

- `200` A [Page](#page) of [Users](#user_object)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

#### Authorization functions

- Using this endpoint requires the `ADMIN_USERS` function.
- Requesting users of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Create user {#create_user}

A user can be created by performing a `POST` request with [CreateUser](#create_user_object) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users
```

#### Response

- `200` Ok. Body: [User](#user_object)
- `400` One or more of the provided property values were not valid

#### Authorization functions

- `ADMIN_USERS`
- Creating a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Retrieve user info {#fetch_user}

You can request the information of a user by performing a `GET` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `200` The [User](#user_object)
- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access their own information.
- A user with the `ADMIN_USERS` function can fetch the information of another user.
- Requesting a user of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Retrieve all info of current user {#full_current_user}

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/current?full=true
```

This will return the same information as the `/current` endpoint with the following extra’s:

- Ingest spaces
- Default Export location id
- Export locations

#### Response

- `200` The current [User](#user_object)
- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access this endpoint.

### Update info of user {#update_user}

Updating the info of a user can be done by performing a `PUT` request with [Update User](#update_user_object) as body
to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `200` Ok. Body: Updated [User](#user_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the user in question or no access to update the email address.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access this endpoint to update their own information.
- A user with the `ADMIN_USERS` function can update the information of another user.
- Updating a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Delete a user {#delete_user}

A user can be deleted by performing a `DELETE` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id
```

#### Response

- `204` The user was deleted.
- `400` One or more of the provided property values were not valid.
- `403` No access to the user in question.
- `404` The user does not exist or one or more of the provided property values (ids) do not exist or the user does not
  have access to them.

#### Authorization functions

- A user with the `ADMIN_USERS` function can delete a user.
- Deleting a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Retrieve all functions assigned to a user {#user_functions}

In order to get a complete list of all the functions assigned to a user, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/functions
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `200` An array containing all functions assigned to the current user.

```json
[
  "<string>"
]
```

- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access their own functions.
- A user with the `ADMIN_USERS` function can fetch the functions of another user.
- Requesting the functions of a user of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Retrieve all zones assigned to a user {#user_zones}

In order to get a complete list of all the zones to which a user has access, do a `GET` request to the following
endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/zones
```

> Note: The id ‘current’ can be used as shorthand for the current user.

See the section on [Zones](#zones) for more information.

#### Response

- `200` Ok. [Page](#page) of [Zones](#zone_datamodel)
- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access their own zones.
- A user with the `ADMIN_USERS` function can fetch the zones of another user.
- Requesting the zones of a user of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Retrieve all groups assigned to a user {#user_groups}

In order to get a complete list of all the groups of a user, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/groups
```

> Note: The id ‘current’ can be used as shorthand for the current user.

See the section on [Groups](#groups) for more information.

#### Response

- `200` Ok. [Page](#page) of [Groups](#group_datamodel)
- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access their own groups.
- A user with the `ADMIN_USERS` function can fetch the groups of another user.
- Requesting the groups of a user of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Retrieve all roles assigned to a user {#user_roles}

In order to get a complete list of all the roles of a user, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/roles
```

> Note: The id ‘current’ can be used as shorthand for the current user.

See the section on [Roles](#roles) for more information.

#### Response

- `200` Ok. [Page](#page) of [Roles](#roles_datamodel)
- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access their own roles.
- A user with the `ADMIN_USERS` and `ADMIN_ALL_ROLES` or `ADMIN_LINK_ROLES` function can fetch the roles of another user.
- Requesting the roles of a user of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.
- Assigning a role containing the function `ADMIN_VIEW_ALL_ORGANISATIONS` requires the caller to have the
  function `ADMIN_VIEW_ALL_ORGANISATIONS`.
- Assigning a role containing the function `ADMIN_EDIT_ALL_ORGANISATIONS` requires the caller to have the
  function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve all export locations assigned to a user {#user_export_locations}

In order to get a complete list of all the export locations of a user, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/export-locations
```

> Note: The id ‘current’ can be used as shorthand for the current user.

See the section on [Export locations](#export_locations) for more information.

#### Response

- `200` Ok. [Page](#page) of [Export locations](#export_locations_object)
- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access their own export locations.
- A user with the `ADMIN_USERS` function can fetch the export locations of another user.
- Requesting the export locations of a user of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS`
  function.

### Retrieve all saved filters of the current user {#user_filters}

In order to get a list of all the saved filters the current user can use, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/current/filters
```

The result includes all filters created by the user or having a matching user group.
See the section on [Filters](#filters) for more information.

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| name | The name of the filter. Wildcards \* are allowed. |  |
| sort | Sort on one of the following fields (`Name`, `CreationDate`, `LastModifiedDate`) | Name |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

#### Response

- `200` A [Page](#page) of [Filters](#filter_object)
- `400` The request is not valid
- `401` User is not authorized

### Update functions of a user {#update_user_functions}

User functions can be updated by performing a `PUT` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/functions
```

with an array of function names:

```json
[
  "<string>",
  ...
]
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `204` The list of functions was updated.
- `403` No access to the user in question.
- `404` The user does not exist or one or more of the functions do not exist.

#### Authorization functions

Updating functions requires the function `ADMIN_ALL_ROLES` or `ADMIN_LINK_ROLES`:

- Any authenticated user can update their own functions.
- Updating the functions of another user requires the `ADMIN_USERS`.
- Updating the functions of a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Update zones of a user {#update_user_zones}

User zones can be updated by performing a `PUT` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/zones
```

with an array of zone ids:

```json
[
  "<uuid of zone>",
  ...
]
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `204` Zones were updated.
- `403` No access to the user or one or more of the zones in question.
- `404` The user does not exist or one or more of the zone ids do not exist.

#### Authorization functions

Updating zones requires the function `ADMIN_ZONES`:

- Any authenticated user can update their own zones.
- Updating the zones of another user requires the `ADMIN_USERS`.
- Updating the zones of a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Update groups of a user {#update_user_groups}

User groups can be updated by performing a `PUT` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/groups
```

with an array of group ids:

```json
[
  "<uuid of group>",
  ...
]
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `204` Groups were updated.
- `403` No access to the user or one or more of the groups in question.
- `404` The user does not exist or one or more of the group ids do not exist.

#### Authorization functions

Updating groups requires the function `ADMIN_GROUPS`:

- Any authenticated user can update their own groups.
- Updating the groups of another user requires the `ADMIN_USERS`.
- Updating the groups of a user of a different organisation or adding a group from a different organisation than the
  user requires the `ADMIN_EDIT_ALL_ORGANISATIONS` or `ADMIN_EXTERNAL_USERS` (legacy) function.

### Update roles of a user {#update_user_roles}

User roles can be updated by performing a `PUT` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/roles
```

with an array of role ids:

```json
[
  "<uuid of role>",
  ...
]
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `204` Roles were updated.
- `403` No access to the user or one or more roles in question.
- `404` The user does not exist or one or more of the role ids do not exist.

#### Authorization functions

Updating roles requires the function `ADMIN_ALL_ROLES` or `ADMIN_LINK_ROLES`:

- Any authenticated user can update their own roles.
- Updating the roles of another user requires the `ADMIN_USERS`.
- Updating the roles of a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Update export locations of a user {#update_user_export_locations}

User export locations can be updated by performing a `PUT` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/export-locations
```

with an array of export location ids:

```json
[
  "<uuid of export location>",
  ...
]
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `204` Export locations were updated.
- `403` No access to the user or one or more export locations in question.
- `404` The user does not exist or one or more of the export location ids do not exist.

#### Authorization functions

Updating export locations requires the function `ADMIN_EXPORTS`:

- Any authenticated user can update their own export locations.
- Updating the export locations of another user requires the `ADMIN_USERS`.
- Updating the export locations of a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS`
  function.

## Update User object structure {#update_user_object}

You can send the full user object but only the following properties can be updated.

Note: Due to this API is designed to be HTTP method PUT, meaning if missing any of Email/FirstName/LastName, then it will be assumed they are NULL.
However, to be more user-friendly, if existing user already has data in db, then there will be 400 BAD Request error returned.

| Property | Type | Description | Readonly | Required | Full | Default value |
| --- | --- | --- | --- | --- | --- | --- |
| Email | String | An email address. Must be a valid format. | No | No |  |  |
| FirstName | String | The first name of the user. | No | No |  |  |
| LastName | String | The last name of the user. | No | No |  |  |
| Locale | String | The locale of the user. Possible values can be retrieved via the [Locales](#locales) endpoint. | No | No |  | Organisation default |

> Note: An email address can only be updated for your own user.

## User object structure {#user_object}

| Property | Type | Description | Readonly | Required | Full | Default value |
| --- | --- | --- | --- | --- | --- | --- |
| Id | String | A unique id. | Yes |  |  |  |
| Login | String | A login name. | Yes |  |  |  |
| Email | String | An email address. Must be a valid format. | No | No |  |  |
| FirstName | String | The first name of the user. | No | No |  |  |
| LastName | String | The last name of the user. | No | No |  |  |
| Organisation | [Organisation](#organisation-object) | The organisation of the user. | Yes |  |  |  |
| Locale | String | The locale of the user. Possible values can be retrieved via the [Locales](#locales) endpoint. | No | No |  | Organisation default |
| Rights |  | The rights of the user. | No (ADMIN_USERS required) |  |  |  |
| Rights.DeleteRights | Boolean | Does the user have delete right. | No (ADMIN_USERS required) |  |  |  |
| Rights.ExportRights | Boolean | Does the user have export right. | No (ADMIN_USERS required) |  |  |  |
| Rights.WriteRights | Boolean | Does the user have write right. | No (ADMIN_USERS required) |  |  |  |
| Rights.ReadRights | Boolean | Does the user have read right. | No (ADMIN_USERS required) |  |  |  |
| UserFunctions | String[] | `Deprecated property, might be removed in the future. Use 'users/:userId/functions' instead.` The UserFunctions of the user. | Yes |  |  |  |
| Roles | [Role](#roles_datamodel)[] | `Deprecated property, might be removed in the future. Use 'users/:userId/roles' instead.` The roles of the user. | Yes |  |  |  |
| Groups | [Group](#group_datamodel)[] | `Deprecated property, might be removed in the future. Use 'users/:userId/groups' instead.` The groups of the user. | Yes |  |  |  |
| IsSystem | Boolean | Whether this is a special user with authorization type different from Normal. See <https://mediahaven.atlassian.net/wiki/spaces/CS/pages/3911581715/Special+Users> for more information. | Yes |  |  |  |
| TenantGroup | String | Property which groups a number of organisations together (DigiHaven only). | Yes |  |  |  |
| IngestSpaces | IngestSpace[] | `Deprecated property, might be removed in the future. Use 'users/:userId/zones' instead.` The ingest spaces of the user. | Yes |  | Yes |  |
| IngestSpaces.Id | String (UUID) | A unique id for the ingest space | Yes |  | Yes |  |
| IngestSpaces.Name | String | A name for the ingest space | Yes |  | Yes |  |
| DefaultExportLocationId | String | The id for the default export location. | Yes |  | Yes |  |
| ExportLocations | [ExportLocation](#export_locations_object)[] | `Deprecated property, might be removed in the future. Use 'users/:userId/export-locations' instead.` The export locations of the user. | Yes |  | Yes |  |
| CreationDate | Date (ISO8601) | The date when the user was created. | Yes |  |  |  |
| LastModifiedDate | Date (ISO8601) | The date when the user was last modified. | Yes |  |  |  |
| LastLoginDate | Date (ISO8601) | The date of the last successful login. | Yes |  |  |  |
| Type | Enum (‘Mediahaven’, ‘Oauth’, ‘Ldap’, ‘Saml’) | The authentication type of the user. Users created via this API, will have type ‘Mediahaven’. | Yes |  |  |  |
| AuthorizationType | Enum (‘Normal’, ‘Application’, ‘Public’, ‘ZeticonPrimaryOrganisation’, ‘ZeticonSecondaryOrganisation’, ‘ZeticonAllOrganisations’, ‘System’, ‘SystemAllOrganisations’) | The authorization type of the user. Users created via this API are only allowed to be ‘Normal’ or ‘Application’ | Yes |  |  | Normal |
| Context.IsEditable | Boolean | Read-only field that indicates if the user is editable. | Yes |  |  |  |
| Context.ArePreferencesEditable | Boolean | Read-only field that indicates if the user preferences are editable. | Yes |  |  |

Example:

```json
{
  "Id": "",
  "Login": "fred",
  "FirstName": "fred",
  "Email": "fred.jones@zeticon.com",
  "LastName": "jones",
  "Organisation": {
    "Id": 1,
    "Name": "Zeticon",
    "LongName": "Zeticon",
    "CustomProperties": {
      "<json>"
    },
    "TenantGroup": "Vlaamse Overheid",
    "ExternalId": "OVO001151"
  },
  "Locale": "en_US",
  "Rights": {
    "DeleteRights": true,
    "ExportRights": true,
    "WriteRights": true,
    "ReadRights": true
  },
  "UserFunctions": [
    "ADMIN_USERS"
  ],
  "Roles": [
    {
      "RoleId": "24192b2e-7e0a-423f-b3a7-724320d62129",
      "Label": "Employee",
      "OrganisationId": 1,
      "Functions": [
        "publish_rights"
      ]
    }
  ],
  "Groups": [
    {
      "Id": "df100b7a-efd0-44e3-8816-0905572421da",
      "Name": "Marketing",
      "OrganisationId": 1,
      "WriteRights": true,
      "ReadRights": true,
      "ExportRights": true,
      "IsSystem": false
    }
  ],
  "IsSystem": false,
  "TenantGroup": "Vlaamse Overheid",
  "LastModifiedDate": "2022-10-18T14:20:21.193000Z",
  "CreationDate": "2022-10-16T14:20:11.000000Z",
  "Type": "MediaHaven",
  "AuthorizationTye": "Normal",
  "Context": {
    "IsEditable": true,
    "ArePreferencesEditable": true
  }
}
```

## Create object structure {#create_user_object}

The body of the create user object is the same as the user object with the addition of the following properties:

| Property | Type | Description | Required | Default value |
| --- | --- | --- | --- | --- |
| Login | String | A login name. | Yes |  |
| Password | String | The password to be used for logging in | Yes |  |
| OrganisationId | Number | The id of the organisation | Yes |  |
| Rights.DeleteRights | Boolean | Can the user delete records | No | False |
| Rights.ExportRights | Boolean | Can the user exports records | No | False |
| Rights.WriteRights | Boolean | Can the user create records | No | False |
| Rights.ReadRights | Boolean | Can the user read records | No | False |
| FirstName | String | First name of the user | No |  |
| LastName | String | Last name of the user | No |  |
| Email | String | Email of the user | No |  |
| Locale | String | Locale of the user | No |  |
| TenantGroup | String | Tenant group of the user | No |

Example:

```json
{
  "Login": "fred",
  "FirstName": "fred",
  "Email": "fred.jones@zeticon.com",
  "LastName": "jones",
  "Locale": "en_US",
  "Rights": {
    "DeleteRights": true,
    "ExportRights": true,
    "WriteRights": true,
    "ReadRights": true
  },
  "TenantGroup": "Vlaamse Overheid",
  "Password": "134",
  "OrganisationId": 100
}
```

## User preferences {#user-preferences}

### Retrieve all preferences of a user {#user_preferences}

The user preferences of a user can be retrieved by sending a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/preferences
```

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `200` Ok. Body: [User preferences](#user_preferences_object)
- `403` No access to the user in question.
- `404` The user does not exist.

#### Authorization functions

- Any authenticated user can access their own preferences.
- A user with the `ADMIN_USERS` function can fetch the preferences of another user.
- Requesting the preferences of a user of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Update preferences of a user {#update_user_preferences}

User preferences can be updated by performing a `PUT` request
with [User preferences](#user_preferences_object)
as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/:id/preferences
```

Preferences that are not explicitly defined in the request will not be changed.

> Note: The id ‘current’ can be used as shorthand for the current user.

#### Response

- `200` Ok. Body: [User preferences](#user_preferences_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the user in question.
- `404` The user does not exist or one or more of the provided property values (ids) do not exist or the user does not
  have access to them.

#### Authorization functions

Updating preferences requires the function `ADMIN_USERS`:

- Any authenticated user can update their own preferences or the preferences of a user of the same organisation.
- Updating the preferences of a user of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### User preferences object structure {#user_preferences_object}

| Property | Description | Default value |
| --- | --- | --- |
| DefaultSortField | The specific field you want to sort on. Possible values:  *`relevance`*  or one of the [sortable metadata fields](#fields_sortable) | relevance |
| DefaultSortDirection | The direction (Asc/Desc) for the SortField | Desc |
| NrOfSearchResults | The number of results that will be returned. Note that this is returned as string. | 25 |
| DefaultClassification | The default classification id. Might not be valid when retrieved, i.e. if the zone been deleted. | null |
| DefaultZone | The default zone id. Might not be valid when retrieved, i.e. if the classification has been deleted. | null |
| DefaultDisplay | The default display. This preference accepts any string value. | null |

Example:

```json
{
  "DefaultSortField": "relevance",
  "DefaultSortDirection": "Desc",
  "NrOfSearchResults": "25",
  "DefaultClassification": "4bf7d6b6-2b52-11ec-8d3d-0242ac130003",
  "DefaultZone": "60aca242-97ff-47d6-97d5-0430a0882042",
  "DefaultDisplay": "Grid"
}
```

## Password management {#password-resource}

### Updating a password {#password_update}

Updating the password of a user can be done by performing a PUT-request with a [Password](#password_body)
as body to:

```http
PUT https://archief.viaa.be/mediahaven-rest-api/v2/users/current/password
```

#### Response

- `200` The password was updated. The user can now log in by using the new password.
- `400` One of the provided parameters was not valid
- `401` User is not authorized

#### Authorization functions

- Any authenticated user can use this endpoint.

### Change password object structure {#password_body}

| Property | Type | Description | Required |
| --- | --- | --- | --- |
| OldPassword | String | The old password. | Yes |
| NewPassword | String | The new password. | Yes |

Example:

```json
{
  "OldPassword": "RainbowsAndKittens1234", // gitleaks:allow
  "NewPassword": "KittensAndRainbows1234" // gitleaks:allow
}
```

### Requesting a password reset {#password_reset}

A password reset for a user can be requested by performing a POST-request with
a [Password reset request](#password_reset_request_body) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/password-resets
```

If the user exists they will receive an e-mail with a password reset link. They have 24 hours to complete the request.

#### Authorization functions

- A user with the `ADMIN_USERS` and `ADMIN_EDIT_ALL_ORGANISATIONS` function has to request this on behalf of the end
  user.

#### Response

- `202` The request was acknowledged

### Completing a password reset {#password_reset}

A password reset for a user can be completed by performing a PUT-request with a [Password reset](#password_reset_body)
as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/password-resets/:code
```

> Note: the code is provided with the link in the email the user receives

#### Response

- `200` The password was updated. The user can now log in by using the new password. [Password reset response](#password_reset_response_body)
- `400` One of the provided parameters was not valid
- `409` When the password reset is no longer active

#### Authorization functions

- A user with the `ADMIN_USERS` and `ADMIN_EDIT_ALL_ORGANISATIONS` function has to request this on behalf of the end
  user.

### Password reset request object structure {#password_reset_request_body}

| Property | Type | Description | Required |
| --- | --- | --- | --- |
| Email | String | An email address. Must be a valid format. | Yes |
| App | String | The app to which the user should be sent after password reset | No |

Example:

```json
{
  "Email": "fred.jones@zeticon.com"
}
```

### Password reset response object structure {#password_reset_response_body}

| Property | Type | Description |
| --- | --- | --- |
| App | String | The app for which the request was done. |

Example:

```json
{
  "App": "mediahaven2"
}
```

### Password reset object structure {#password_reset_body}

| Property | Type | Description | Required |
| --- | --- | --- | --- |
| Email | String | The email address the reset was requested for. | Yes |
| Password | String | The new password. | Yes |

Example:

```json
{
  "Email": "fred.jones@zeticon.com",
  "Password": "KittensAndRainbows1234" // gitleaks:allow
}
```

## Personal selection {#personal-selections}

The personal selection is an object that is coupled with a specific user. This records contains a reference to a list of
other records. This allows the user to temporarily create a list of records to i.e. download all at once.

Note that selections are a special type of [Record](#record-object), so all objects returned by this endpoint follow the
record model.

The difference between a personal selection and a [generic selection](#generic-selections) is that there is only 1
personal selection per user.

### Required functions {#mediahaven-rest-api-manual-personal-selection-required-functions}

Any authenticated user can access their own personal selection. This does not require read or write permissions.

### Properties {#mediahaven-rest-api-manual-personal-selection-properties}

Selections have the following noteworthy properties

| Metadata Field | Description |
| --- | --- |
| `Internal.UploadedBy` | The name of the user that created the selection. |
| `Internal.UploadedById` | The id of the user that created the selection. |
| `Administrative.RecordType` | `Selection.Personal` |
| `Structural.Relations.Contains` | The records contained in this selection |

The equivalent `application/json` is

```json
{
  "Internal": {
    "RecordId": "2ae64fa5dc6147239f8956ed4049eb7cfd55a00695f24136b2ee826a99c3419a",
    "UploadedBy": "a0f3aa33-c351-4d73-9bf1-ad93ac198b0f"
  },
  "Administrative": {
    "OrganisationName": "mh-dev",
    "RecordStatus": "Published",
    "RecordType": "Selection.Personal"
  },
  "Context": {
    "IsEditable": true,
    "IsDeletable": true,
    "IsPublic": false,
    "IsExportable": true,
    "Profiles": []
  }
}
```

### Getting the personal selection {#personal-selection-creation}

The personal selection can be retrieved by doing a `GET` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/users/current/selection
```

#### Response

- `200` Ok: [Record](#record-object)

### Updating the personal selection {#personal-selection-add-records}

The personal selection can be updated by sending a `POST`request to:

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/users/current/selection
```

with as body of content type `application/json` with properties

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| RecordsStrategy | ENUM | The merge strategy to apply to the list of record. See [this section](#edit_metadata) for more info. | MERGE | No |
| Records | String[] | List of records to add to the selection. | Empty array | Yes |

#### Example body

```json
{
  "Records": [
    "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1"
  ]
}
```

#### Response

- `201` Created: [Record](#record-object)
- `400` Bad request: [Error result](#error)
- `403` Forbidden: [Error result](#error)
- `412` Precondition Failed:
    - When
      a [metadata collision](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/5070487629/Version+Conflict+Detection)
      occurs

## Generic selections {#generic-selections}

With selections you can share group records together in order to i.e. share them easily without downloading/exporting
them.

The difference between a generic selection and a [personal selection](#personal-selection) is that users can freely
create multiple generic solutions.

### Required functions {#mediahaven-rest-api-manual-generic-selections-required-functions}

Any authenticated user can create selections.

### Properties {#mediahaven-rest-api-manual-generic-selections-properties}

Selections have the following noteworthy properties

| Metadata Field | Description |
| --- | --- |
| `Descriptive.CreationDate` | The date the selection was added |
| `Internal.UploadedBy` | The name of the user that created the selection. |
| `Internal.UploadedById` | The id of the user that created the selection. |
| `Internal.RecordId` | The unique ID of the selection |
| `Administrative.RecordType` | `Selection.Generic` |
| `Structural.Relations.Contains` | The records contained in this selection |

The equivalent `application/json` is

```json
{
  "Descriptive": {
    "CreationDate": "2021-05-21T08:14:23.000000Z"
  },
  "Internal": {
    "RecordId": "2ae64fa5dc6147239f8956ed4049eb7cfd55a00695f24136b2ee826a99c3419a",
    "UploadedBy": "a0f3aa33-c351-4d73-9bf1-ad93ac198b0f"
  },
  "Administrative": {
    "OrganisationName": "mh-dev",
    "RecordStatus": "Published",
    "RecordType": "Selection.Generic"
  },
  "Context": {
    "IsEditable": true,
    "IsDeletable": true,
    "IsPublic": false,
    "IsExportable": true,
    "Profiles": []
  }
}
```

### Model {#mediahaven-rest-api-manual-generic-selections-model}

Selections are specialised records and hence an extension on the existing endpoints for

- [search on records](#search-for-media-objects)
- [delete records](#delete)

The returned objects are [Records](#record-object).

### Creating a generic selection {#generic-selection-creation}

Create a new generic selection by doing a `POST`

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/generic-selections
```

with as body of content type `application/json` with properties

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| RecordsStrategy | ENUM | The merge strategy to apply to the list of record. See [this section](#edit_metadata) for more info. | MERGE | No |
| Records | String[] | List of records to add to the selection. | Empty array | Yes |

#### Example

```json
{
  "Records": [
    "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1"
  ]
}
```

Notes:

-
- A maximum of 500 items can be added to `Records`

#### Response

- `201` Created: [Record](#record-object)
- `400` Bad request: [Error result](#error)
- `403` Forbidden: [Error result](#error)

### Updating the personal selection {#generic-selection-add-records}

The personal selection can be updated by sending a `POST`request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/generic-selections/:id
```

Options are the same as when creating a selection.

#### Response

- `200` Ok: [Record](#record-object)
- `400` Bad request: [Error result](#error)
- `403` Forbidden: [Error result](#error)
- `412` Precondition Failed:
    - When
      a [metadata collision](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/5070487629/Version+Conflict+Detection)
      occurs

### Searching {#selections-generic-searching}

To list all generic selections, make a `GET` request using the same parameters as for [records](#basic-searching).

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/generic-selections?q=%2b(UploadedBy:a0f3aa33-c351-4d73-9bf1-ad93ac198b0f)&startIndex=0&nrOfResults=5
```

The syntax of this endpoint is exactly the same as for [records](#basic-searching) but only records
having `RecordType:Selection.Generic` are returned.

### Getting a specific selection {#selections-generic-get}

To get a specific selection, make a `GET` request using its `RecordId`

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/generic-selections/:recordId
```

The syntax is exactly the same as for [records](#get_record) but it will raise
`400` Bad request when the record has a `RecordType` different from `Selection.Generic`.

### Deleting a selection {#selections-generic-delete}

To remove a selection, make a `DELETE` request using its `RecordId`

```http
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/generic-selections:recordId
```

The syntax is exactly the same as for [records](#deleting) but it will raise
`400` Bad request when the record has a `RecordType` different from `Selection.Generic`

## Supported locales {#locales}

This endpoint is used for retrieving all locales that can be configured on a [User](#user-resource).

### Listing all supported locales {#get_locales}

Retrieve an array of strings representing all supported locales using a `GET` request

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/locales
```

#### Response

- `200` Ok. Body: list of strings.

Example response:

```json
[
  "nl_BE",
  "en_US",
  "fr_BE",
  "de_DE"
]
```

#### Authorization functions

- Any authenticated user can access this resource

## User groups {#groups}

Groups are used to determine the permissions of a user. When a user is a member of a group, he can view, edit or export
the records that are managed by the group, depending on the specific settings of the rights.

### Required functions {#group_functions}

- The user requires the `ADMIN_GROUPS` function to access this endpoint.
- By default, only groups within the same
  organisation as the user are accessible.
- Accessing groups from other organisations requires the `ADMIN_VIEW/EDIT_ALL_ORGANISATIONS` function.

### UserGroup object structure {#group_datamodel}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Id | String (UUID) | A unique group id. | Yes |  |  |
| Name | String | A name to describe the group. Must be unique per organisation. | No | Empty | Yes |
| OrganisationId | Number | The id of the organisation the group belongs to. | No | Organisation of the user | No |
| ReadRights | Boolean | Determines if users in this group can view records. | No | false | No |
| WriteRights | Boolean | Determines if users in this group can edit records.  Can only be set to true if ReadRights is set to true. | No | false | No |
| ExportRights | Boolean | Determines if users in this group can export files.  Can only be set to true if ReadRights is set to true. | No | false | No |
| IsSystem | Boolean | Denotes that the group is a default system group.   System groups can be updated, but cannot be deleted.   Note: Groups of type ‘Zone’ can NOT be updated. | Yes |  |  |
| Type | Enum | Enum value that contains one of the following values:  - Normal   - Public   - Global   - System   - Administrator   - Organisation   - Zone | Yes |  |  |
| CreationDate | Date (ISO8601) | The date when the group was created. | Yes |  |  |
| LastModifiedDate | Date (ISO8601) | The date when the group was last modified. | Yes |  |

> Note: These settings are used as a default but can be overwritten when uploading assets. Please refer to the [organisational structures](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/837615626/Organisational+Structures) documentation for more information on this topic.

Example:

```json
{
  "Id": "60aca242-97ff-47d6-97d5-0430a0882042",
  "Name": "1",
  "OrganisationId": 100,
  "WriteRights": true,
  "ReadRights": true,
  "ExportRights": false,
  "IsSystem": false,
  "Type": "Normal",
  "LastModifiedDate": "2022-10-18T14:20:21.193000Z",
  "CreationDate": "2022-10-16T14:20:11.000000Z"
}
```

### Create group {#create_group}

To create a new user group you can send a `POST` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/
```

The endpoint support json and xml with the following properties:

#### UserGroup object structure {#create_group_datamodel}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Name | String | A name to describe the group. Must be unique per organisation. | No | Empty | Yes |
| OrganisationId | Number | The id of the organisation the group belongs to. | No | Organisation of the user | No |
| ReadRights | Boolean | Determines if users in this group can view records. | No | false | No |
| WriteRights | Boolean | Determines if users in this group can edit records.  Can only be set to true if ReadRights is set to true. | No | false | No |
| ExportRights | Boolean | Determines if users in this group can export files.  Can only be set to true if ReadRights is set to true. | No | false | No |
| AddUsers | Boolean | `Deprecated property, no longer allowed to be true.` If set to true, all users for the organisation are added to the group. | No | false | No |

Example request body:

```json
{
  "Name": "Marketing",
  "OrganisationId": 100,
  "ReadRights": true,
  "WriteRights": true,
  "ExportRights": true,
  "AddUsers": false
}
```

All groups created this way will be of Type ‘Normal’.

When AddUsers is set to true, all users for the organisation are added to the group. Requires the function ADMIN_USERS.

### Updating a group {#update_group}

Updating a group can be done by performing a `PUT` request with a [Group](#group_datamodel) as body to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/:id
```

The endpoint supports json and xml.

### Adding user(s) to a group {#group_add_users}

One or more users can be added to a group by performing a `POST` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/:id/users
```

with an array with the user ID(s)

```json
[
  "<uuid of user>",
  ...
]
```

> Note: Only 20 users can be added within a single request.
> Note: Adding users to a group of type `ZONE` is not allowed.

#### Response

- `204` Users were added.
- `400` No users IDs are in the list.
- `400` The number of users is more than the number allowed within a single request.
- `403` The user does not have the required functions to call this method.
- `403` The group is of type `ZONE`.
- `404` The group does not exist or one or more of the user ids do not exist.

#### Authorization functions

In addition to the functions [above](#group_functions), adding users requires the following functions:

- Always required: `ADMIN_USERS`
- Adding a user from a different organisation than the group requires the `ADMIN_EDIT_ALL_ORGANISATIONS`
  or `ADMIN_EXTERNAL_USERS` (legacy) function.

### Deleting a group {#delete_group}

Deleting a group is done by simple sending a `DELETE` request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/:id
```

> Note: Deleting protected groups, namely those with the type different from `NORMAL`, is forbidden

### Removing user(s) from a group {#group_delete_users}

One or more users can be removed from a group by performing a `DELETE` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/:id/users
```

with an array with the user ID(s)

```json
[
  "<uuid of user>",
  ...
]
```

> Note: Only 20 users can be added within a single request.
> Note: Adding users to a group of type `ZONE` is not allowed.

#### Response

- `204` Users were removed.
- `400` No users IDs are in the list.
- `400` The number of users is more than the number allowed within a single request.
- `403` The user does not have the required functions to call this method.
- `403` The group is of type `ZONE`.
- `404` The group does not exist or one or more of the user ids do not exist.

#### Authorization functions

In addition to the functions [above](#group_functions), removing users requires the following functions:

- Always required: `ADMIN_USERS`
- Removing a user from a different organisation than the group requires the `ADMIN_EDIT_ALL_ORGANISATIONS`
  or `ADMIN_EXTERNAL_USERS` (legacy) function.

### Getting a specific group {#get_group}

Getting a specific group is done by sending a `GET` request to the following url.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/:id
```

### Listing all groups {#get_all_groups}

A list of all groups can be retrieved using a `GET` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Organisation to search in. Required function `ADMIN_VIEW_ALL_ORGANISATIONS` if searching in other organisations. | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| type | Search for groups of this type |  |
| name | Name of the group. Wildcards \* are allowed. |  |
| id | Id of group |  |
| sort | Sort on one of the following fields (Name, Id, CreationDate, LastModifiedDate) | Name |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

#### Response

- `200` Ok. [Page](#page) of [Groups](#group_datamodel)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

### Get number of users linked to group {#get_users_group_count}

To get the total number of users linked to a group, do a `HEAD` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/:id/users
```

The response will contain a header element with the name `Result-Count`.

#### Response

- `200` Ok.
- `401` User is not authorized
- `403` No access to the group in question.
- `404` The group does not exist.

### Listing all users assigned to a group {#group_users}

In order to get a complete list of all the users of a group, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/groups/:id/users
```

The standard [Page parameters](#page-filter) are available.

#### Response

- `200` Ok. [Page](#page) of [Users](#user_object)
- `403` No access to the group in question.
- `404` The group does not exist.

## Roles and functions {#roles}

Roles and functions taken together provide a fine-grained access control model to MediaHaven.

Functions in particular are used to determine the parts of MediaHaven a user has access to. This includes, for example,
functions that provide access to different parts of the administrator module.

A role is essentially a collection of functions that can be assigned to one or more users. Roles can be defined on two
levels.

- Global roles can be assigned to users across the entire system.
- Roles can be defined for a particular organisation, meaning they can only be assigned to users belonging to that
  organisation.

The next few subsections will explain how to get a list of all functions and how to list, create, and edit roles.

### Listing all functions {#function_list}

A list of all possible functions can be retrieved by sending a `GET` call to the following endpoint.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/functions
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| onlyAssignable | If true, only functions that can be assigned via the api to users, roles or organisation default roles are returned | false |

The response will be a list of functions.

```json
[
  "ADMIN_EXPORTS",
  "ADMIN_EXTENSIONS"
]
```

### Get number of users linked to a function {#get_users_function_count}

To get the total number of users linked to a function, do a `HEAD` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/functions/:function/users
```

The response will contain a header element with the name `Result-Count`.

#### Response

- `200` Ok.
- `401` User is not authorized
- `403` No access to the function in question.
- `404` The function does not exist.

### List all roles {#role_list}

A list of all roles can be retrieved by sending a `GET` request to the following endpoint.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/roles
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| sort | Sort on one of the following fields (CreationDate, LastModifiedDate) | CreationDate |
| direction | The direction can be `asc`, `up`, `desc` or `down` | desc |
| organisationId | Organisation to search in | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| label | Search on label of role |  |
| onlyAssignable | If true, only roles that can be assigned via the api to users or organisation defaults are returned | false |

#### Response

- `200` A list of [Roles](#roles_datamodel)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

#### Authorization functions

- Requesting roles of all organisations requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Get number of users linked to role {#get_users_role_count}

To get the total number of users linked to a role, do a `HEAD` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/roles/:id/users
```

The response will contain a header element with the name `Result-Count`.

#### Response

- `200` Ok.
- `401` User is not authorized
- `403` No access to the role in question.
- `404` The role does not exist.

### Get a specific role {#role_get}

To get a specific role, make a `GET` call to the following endpoint

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId
```

### Deleting a role {#role_delete}

To delete a role, make a `DELETE` request to the following endpoint.

```http
https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId
```

This will return a response with status code `204` if successful

### Creating a role {#role_create}

Creating a new role can be done by sending a `POST` request to following endpoint. The body should contain
a [roles-object](#roles_datamodel)

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/roles/
```

### Update an existing role {#role_update}

To edit the label of a role, send a `PUT` with a [Role](#roles_datamodel) to the following endpoint.

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId
```

It is not possible to change the organisation id of an existing role.

### Get all functions for a role {#role_get_functions}

To get all the functions for a role, make a `GET` request to the following endpoint.

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId/functions
```

Note that the list of functions is also returned when getting all info for [a specific role](#role_get).

### Changing the label of a role {#role_change_label}

To change the label of a role, make a `POST` request to the following endpoint with the label as body.

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId/label
```

### Adding functions to a role {#role_add_functions}

To add functions to a role, make a `POST` request to the following endpoint

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId/functions
```

with an array with the function names:

```json
[
  "<string>",
  ...
]
```

All the functions must already have been defined. Otherwise the entire request will fail.

### Removing a function from a role {#role_remove_functions}

To remove a function from a role, make a `DELETE` request to the following endpoint

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId/functions/:functionName
```

#### Possible responses

`200` Function is removed from the role
`400` Function does not exist or is not part of this role
`403` User does not have access to this role

#### Required functions {#roles_functions}

For adding or modifying existing roles the `ADMIN_ALL_ROLES` function is required.

### Listing user(s) from a role {#role_list_users}

To list all users linked to a role, do a `GET` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId/users
```

The standard [Page parameters](#page-filter) are available.

#### Authorization functions

- Using this endpoint requires the `ADMIN_USERS` or `ADMIN_LINK_ROLES` function.

#### Response

- `200` A [Page](#page) of [Users](#user_object).
- `401` User is not authorized
- `403` if the user does not have the required functions to call this method
- `404` The role does not exist.

### Adding user(s) to a role {#role_add_users}

To add one or more users to a role, make a `POST` request to the following endpoint

```http
https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId/users
```

with an array with the user ID/user IDs

```json
[
  "<uuid of user>",
  ...
]
```

Possible responses

- `204` if successful
- `400` if no users IDs are in the list
- `400` if more users are added to the list than the given limit, currently 20
- `403` if the user does not have the required functions to call this method
- `404` if the roleId is not found
- `404` if one or more users are not found

#### Authorization functions {#roles_functions}

For adding users to a role the `ADMIN_ALL_ROLES` and `ADMIN_USERS` or `ADMIN_LINK_ROLES` functions are required.

- Adding users to a global role is possible

    - You can add users from your own organisation
    - You can add users from other organisations if you possess the role `ADMIN_EDIT_ALL_ORGANISATIONS`
    - if you try to add users outside your organisation without the specified function a `403` response will be returned
- Adding users to an organisation specific role is possible

    - Only users who are a part of that organisation can be added
    - if you try to add users outside your organisation a `403` response will be returned

### Removing user(s) from a role {#role_rem_users}

To remove one or more users from a role, make a `DELETE` request to the following endpoint

```http
https://archief.viaa.be/mediahaven-rest-api/v2/roles/:roleId/users
```

with an array with the user ID/user IDs

```json
[
  "<uuid of user>",
  ...
]
```

Possible responses

- `204` if successful
- `400` if no users IDs are in the list
- `400` if more users are added to the list than the given limit, currently 20
- `403` if the user does not have the required functions to call this method
- `404` if the roleId is not found
- `404` if one or more users are not found

#### Authorization functions {#roles_functions}

For removing users from a role the `ADMIN_ALL_ROLES` and `ADMIN_USERS` or `ADMIN_LINK_ROLES` functions are required.

- Removing users from a global role is possible

    - You can remove users from your own organisation
    - You can remove users from other organisations if you possess the function `ADMIN_EDIT_ALL_ORGANISATIONS`
    - if you try to remove users outside your organisation without the specified function a `403` response will be
      returned
- Removing users from an organisation specific role is possible

    - Only users who are a part of that organisation can be removed
    - if you try to remove users outside your organisation a `403` response will be returned

## Roles object structure {#roles_datamodel}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| RoleId | String (UUID) | The identifier of the role |  |  |
| Label | String | The label for the role. |  | Yes |
|  |  | - Global roles must have a label unique to the MediaHaven environment |  |  |
|  |  | - Roles assigned to an organisation must have a label unique to that organisation. |  |  |
| OrganisationId | Number | The id of the organisation the roles belongs to. If not included, role will be defined as global. |  |  |
| Functions | String[] | The set of functions that the role will provide | Empty list |  |
| CreationDate | Date (ISO8601) | The date when the role was created. |  | Yes |
| LastModifiedDate | Date (ISO8601) | The date when the role was last modified. |  | Yes |

Example:

```json
{
  "RoleId": "9430ddb5-cedb-4fff-b1ba-f61f96828166",
  "Label": "ARCHIVE_MANAGER",
  "OrganisationId": null,
  "Functions": [
    "CREATE_DOSSIER",
    "EDIT_DOSSIER",
    "VIEW_DOSSIER",
    "DOWNLOAD_DOSSIER",
    "PUBLISH_RIGHTS",
    "VIEW_UNPUBLISHED_DOSSIER",
    "DELETE_DOSSIER",
    "SUBMIT_DOSSIER",
    "EDIT_RELATIONS",
    "VIEW_EVENTS"
  ],
  "LastModifiedDate": "2022-10-18T14:20:21.193000Z",
  "CreationDate": "2022-10-16T14:20:11.000000Z"
}
```

## Profiles {#profiles}

Profiles can be used to group additional fields and make them required for certain records.

You can’t link profiles directly to a record. For this you need to create a top-record (ex. Collection)
To this collection you can link a profile. After linking the profile you can create a new child-record with the
following required metadata.

```json
{
  "Relations": {
    "ChildOf": "<umid of top-record>"
  }
}
```

### Creating a profile {#profiles_create}

Profiles can be created by performing a POST-request with [Profile](#create_profile_object) as body to:

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/profiles
```

#### Response

- `201` The created [Profile](#profile_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function

#### Authorization functions

- Using this endpoint requires the `ADMIN_PROFILES` function.

### Updating a profile {#profiles_update}

Updating a profile can be done by performing a PUT-request with [Profile](#create_profile_object) as body to:

```http
PUT https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId
```

#### Response

- `204` The profile was updated
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the profile
- `404` The profile could not be found

#### Authorization functions

- Using this endpoint requires the `ADMIN_PROFILES` function.

### Deleting a profile {#profiles_delete}

A profile can be deleted by performing a `DELETE`-request to:

```http
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId
```

#### Response

- `204` The profile was deleted
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the profile
- `404` The profile could not be found

#### Authorization functions

- Using this endpoint requires the `ADMIN_PROFILES` function.

### Getting all profiles {#profiles_get_all}

Retrieve a [Page](#page) of [Profiles](#profile_object) using a `GET` request:

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/profiles
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Organisation to search in | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| category | Category to search for |  |
| tag | Tag of profile |

#### Response

- `200` A [Page](#page) of [Profiles](#profile_object)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

#### Authorization functions

- Any authenticated user can access this resource
- `ADMIN_VIEW_ALL_ORGANISATIONS` is needed when searching in other organisations

### Getting a specific profile {#profiles_get_single}

A single [Profile](#profile_object) can be fetched by performing a `GET` request to:

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId
```

#### Response

- `200` Single [Profile](#profile_object)
- `403` User has no access to the profile
- `404` The profile could not be found

#### Authorization functions

- Any authenticated user can access this resource

### Creating a profile field {#profiles_field_create}

Profile fields for a specific profile can be created by performing a `POST`-request
with [Profile field](#create_profile_field_object) as body to:

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId/fields
```

#### Response

- `201` The created [Profile field](#profile_field_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function
- `404` The profile could not be found

#### Authorization functions

- Using this endpoint requires the `ADMIN_PROFILES` function.
- For profiles of `Category`=`MetadataTranslation` the function `ADMIN_METADATA_TRANSLATIONS` is sufficient as well.
- Accessing profiles from other organisations requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Updating a profile field {#profiles_field_update}

Updating a profile field for a specific profile can be done by performing a `PUT`-request
with [Profile field](#create_profile_field_object) as body to:

```http
PUT https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId/fields/:dottedKey
```

> Note: Updating a profile field by `fieldDefinitionId` is deprecated, use `dottedKey` instead.

#### Response

- `204` The profile field was updated
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the profile
- `404` The profile (field) could not be found

#### Authorization functions

- Using this endpoint requires the `ADMIN_PROFILES` function.
- For profiles of `Category`=`MetadataTranslation` the function `ADMIN_METADATA_TRANSLATIONS` is sufficient as well.
- Accessing profiles from other organisations requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Deleting a profile field {#profiles_field_delete}

A profile field for a specific profile can be deleted by performing a `DELETE`-request to:

```http
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId/fields/:dottedKey
```

> Note: Deleting a profile field by `fieldDefinitionId` is deprecated, use `dottedKey` instead.

#### Response

- `204` The profile field was deleted
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the profile
- `404` The profile (field) could not be found

#### Authorization functions

- Using this endpoint requires the `ADMIN_PROFILES` function.
- Accessing profiles from other organisations requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Getting all profile fields {#profiles_field_get_all}

Retrieve a list of [Profile fields](#profile_field_object) for a specific profile using a `GET` request

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId/fields
```

#### Response

- `200` A list of [Profile fields](#profile_field_object)
- `403` User has no access to the profile
- `404` The profile could not be found

#### Authorization functions

- Any authenticated user can access this resource
- Accessing profiles from other organisations requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Getting a specific profile field {#profiles_field_get_single}

A single [Profile field](#profile_field_object) can be fetched by performing a `GET` request to:

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/profiles/:profileId/fields/:dottedKey
```

> Note: Getting a profile field by `fieldDefinitionId` is deprecated, use `dottedKey` instead.

#### Response

- `200` Single [Profile field](#profile_field_object)
- `403` User has no access to the profile
- `404` The profile (field) could not be found

#### Authorization functions

- Any authenticated user can access this resource
- Accessing profiles from other organisations requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Profile object structure {#profile_object}

| Property | Description | Type | Default Value | Required |
| --- | --- | --- | --- | --- |
| Id | The unique identifier of this profile | String (UUID) |  | yes |
| OrganisationId | The organisation id for which this profile should be created (if null the profile is global) | Integer |  | only if category = ‘Facet’ |
| RecordTypes | Record types the profile can be applied to. If the array is empty, the profile can be applied to all records | List | empty | no |
| Name | The name of the profile that matches with the current user locale | String |  | yes |
| Names > Lang | The locale for the name | String |  | yes |
| Names > Value | The actual name for the given locale, if not defined, a fallback will be used | String |  | yes |
| Description | The description of the profile that matches with the current user locale | String |  | yes |
| Descriptions > Lang | The locale for the description | String |  | no |
| Descriptions > Value | The actual description for the given locale, if not defined, a fallback will be used | String |  | no |
| Fields | The fields linked to this profile ([profile field](#profile_field_object)) | List |  | no |
| Category | A group of field related items: Base, AdvancedSearch, GenericList, Facet, Classification, Export, Ai and MetadataTranslation. Each category also has different options | Enum | Base | no |
| Tag | The tag for the profile | String |  | no |
| Row | Row of the profile. Must have value >= 0. Only allowed for profiles with category Base. | Integer |  | Only if Column is defined. |
| Column | Column of the profile. Must have value >= 0. Only allowed for profiles with category Base. | Integer |  | Only if Row is defined. |

Notes:
- `Names` and `Descriptions` contains translations for each supported locale. If no translation is defined for a specific locale, a fallback will be used, namely the first non-empty value from the following list:
- The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
- The translation for the ‘overall’ default locale `en_US`
- Empty value

```json
{
  "Name": "Mijn profiel",
  "Names": [
    {
      "Lang": "en_US",
      "Value": "My profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn profiel"
    }
  ],
  "Id": "b9f25e12-8e49-11eb-8dcd-0242ac130003",
  "OrganisationId": 100,
  "RecordTypes": [
    "Classification"
  ],
  "Description": "Mijn mooi profiel",
  "Descriptions": [
    {
      "Lang": "en_US",
      "Value": "My beautiful profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn mooi profiel"
    }
  ],
  "Fields": [
    "<Profile field>"
  ],
  "Category": "AdvancedSearch"
}
```

### Create profile object structure {#create_profile_object}

| Property | Description | Type | Default Value | Required |
| --- | --- | --- | --- | --- |
| OrganisationId | The organisation id for which this profile should be created (if null the profile is global) | Integer |  | only if category = ‘Facet’ |
| RecordTypes | Record types the profile can be applied to. If the array is empty, the profile can be applied to all records | List | empty | no |
| Names > Lang | The locale for the name | String |  | yes |
| Names > Value | The actual name for the given locale | String |  | yes |
| Descriptions > Lang | The locale for the description | String |  | no |
| Descriptions > Value | The actual description for the given locale | String |  | no |
| Fields | The fields that need to be linked to this profile ([create profile field](#create_profile_field_object)) | List |  | no |
| Category | A group of field related items: Base, AdvancedSearch, GenericList, Facet, Classification, Export, Ai and MetadataTranslation. Each category also has different options | Enum | Base | no |
| Tag | The tag for the profile | String |  | no |
| Row | Row of the profile. Must have value >= 0. Only allowed for profiles with category Base. | Integer |  | Only if Column is defined. |
| Column | Column of the profile. Must have value >= 0. Only allowed for profiles with category Base. | Integer |  | Only if Row is defined. |

```json
{
  "Names": [
    {
      "Lang": "en_US",
      "Value": "My profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn profiel"
    }
  ],
  "OrganisationId": 100,
  "RecordTypes": [
    "Classification"
  ],
  "Descriptions": [
    {
      "Lang": "en_US",
      "Value": "My beautiful profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn mooi profiel"
    }
  ],
  "Fields": [
    {}
  ],
  "Category": "Base"
}
```

### Profile field object structure {#profile_field_object}

#### Default properties {#profile_field_default_properties}

Properties applicable for each category:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| FieldDefinitionId | `Deprecated property, might be removed in the future. Use DottedKey instead` Id of field definition | Integer |  | yes (if DottedKey not defined) |  |
| DottedKey | Dotted key of field definition | String |  | yes (if FieldDefinitionId not defined) |  |
| ReadOnly | Is the field modifiable by the user | Boolean | false | no |  |
| Required | Should it be displayed as required | Boolean | false | no |  |
| Public | `Obsolete property, has no longer any effect. Use Scope instead.` | Boolean | true | no |  |
| Label | The label from Labels that matches with the current user locale | String |  | no | yes |
| DisplayLabel | The value of Label if not empty, otherwise the translation from the field definition that matches with the current user locale. | String |  | no | yes |
| Description | The description from descriptions that matches with the current user locale | String |  | no | yes |
| Labels > Lang | The locale for the label | String |  | no |  |
| Labels > Value | The actual label for the given locale, if not defined, a fallback will be used | String |  | no |  |
| Descriptions > Lang | The locale for the description | String |  | no |  |
| Descriptions > Value | The actual description for the given locale, if not defined, a fallback will be used | String |  | no |  |
| Tag | The tag for the profile | String |  | no |  |
| Control | Indicates which control to use for profile field. This property accepts any string value. | String |  | no |

Notes:
- `Labels` and `Descriptions` contains translations for each supported locale. If no translation is defined for a specific locale, a fallback will be used, namely the first non-empty value from the following list:
- The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
- The translation for the ‘overall’ default locale `en_US`
- Empty value
- `Public` property is obsolete and no longer has any effect. Property `Scope` must be used instead. This property is
  only applicable for [Classification](#profile_field_classification_properties) profiles.

```json
{
  "FieldDefinitionId": 123,
  "DottedKey": "Dynamic.Label",
  "ReadOnly": false,
  "Required": true,
  "Label": "Mijn label",
  "Labels": [
    {
      "Lang": "nl_BE",
      "Value": "Mijn label"
    }
  ],
  "DisplayLabel": "Mijn label",
  "Description": "Mijn beschrijving",
  "Descriptions": [
    {
      "Lang": "nl_BE",
      "Value": "Mijn beschrijving"
    }
  ],
  "Control": "PersonsControl"
}
```

#### GenericList properties {#profile_field_genericlist_properties}

Properties only applicable for category `GenericList`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| DefaultVisible | Show a column by default or not in a generic list | Boolean | true | no | no |

```json
{
  "DefaultVisible": false
}
```

#### Facet properties {#profile_field_facet_properties}

Properties only applicable for category `Facet`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| SelectionType | The type of selection. `SHOULD`: at least one selected value must match. `MUST`: all selected values must match. | Enum | MUST | no | no |
| HideEmpty | Indicates if the empty facets are hidden. | Boolean | false | no | no |
| Sort | On what a facet is sorted. Possible values are `MostFrequent`, `Alphabetically`, `Chronologically`, `FixedOrder`. | Enum | depends on the field definition type | no | no |
| ReverseOrder | Sort the results in reverse order. Can only be true if Sort = `Chronologically`. | Boolean | false | no | no |
| DefaultNumberOfValues | The number of facets to show. Must be in range [1,100]. | Number | 10 | no | no |
| IncludeMissingValue | Include the missing value (e.g. `No Keywords`). | Boolean | true | no | no |
| IncludeActiveValues | Include values which are already selected. | Boolean | false | no | no |

Notes:
- The following rules apply to the `Sort` property:
- Value `Alphabetically` is not applicable for profile fields having a field definition with type `DateField`.
- Value `Chronologically` is only applicable for profile fields having a field definition with type `DateField`.
- Value `FixedOrder` is only applicable for profile fields having a field definition with type `EnumField`: values are sorted in the order in which the possible values are defined on the field definition.
- The default value for date fields is `Chronologically`, for enum fields `FixedOrder` and for other fields `MostFrequent`.
- If `SelectionType` = `SHOULD`, the following applies: if a facet value is selected, this will affect the counts of all facets, except the facet itself. `SHOULD` is not applicable for date fields.
- For property `IncludeActiveValues`, the following applies:
- When searching for facets via the [legacy endpoint](#facet_post_legacy), values that appear as pure MUST terms in the query (e.g. +Descriptive.Keywords.Keyword:Cork) are only returned if `IncludeActiveValues` = true
- When searching for facets via the [preferred endpoint](#facet_post_preferred), values present in the [Bucket](#sq_facet_bucket_object) of the [structured query](#structured_query_object) are only returned if `IncludeActiveValues` = true
- Property has no effect on date facet fields.

```json
{
  "SelectionType": "SHOULD",
  "HideEmpty": true,
  "Sort": "MostFrequent",
  "DefaultNumberOfValues": 10,
  "IncludeMissingValue": false,
  "IncludeActiveValues": true
}
```

#### Classification properties {#profile_field_classification_properties}

Properties only applicable for category `Classification`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| Scope | The scope of the field. Possible values are `Public`, `Standard` and `Advanced`. | Enum | Public | yes | no |
| ChildrenToDisplay | List of child fields, specified by the key, to display in the user interface. Only allowed on fields of type MapField or MultiItemField. | List of strings | [] | no | no |

```json
{
  "Scope": "Standard",
  "ChildrenToDisplay": [
    "Author",
    "Artist"
  ]
}
```

Note: The `Scope` property controls the permissions on a field:

- Reading a field with Scope =  requires the function `VIEW_<SCOPE>_FIELDS` (e.g. `VIEW_STANDARD_FIELDS`).
- Editing a field with Scope =  requires the function `EDIT_<SCOPE>_FIELDS` (e.g. `EDIT_STANDARD_FIELDS`).
- If a field is defined in different profiles with a different scope, the user must have at least one corresponding
  view / edit function in order to view / edit the field.

### MetadataTranslation properties {#profile_field_metadata_translation_properties}

Properties only applicable for category `MetadataTranslation`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| TranslationKeys | The translation keys to use when burning in this field. At least one must be defined. | List | *null* | yes | no |

You can use the metadata translations API to obtain the possible [translation keys](#metadata_translations_get_keys).

```json
{
  "TranslationKeys": [
    "XMP_Title",
    "XMP_Comment"
  ]
}
```

### Create profile field object structure {#create_profile_field_object}

#### Default properties {#create_profile_field_default_properties}

Properties applicable for each category:

| Property | Description | Type | Default Value | Required |
| --- | --- | --- | --- | --- |
| FieldDefinitionId | `Deprecated property, might be removed in the future. Use DottedKey instead` Id of field definition that needs to be added to the profile. You can either provide FieldDefinitionId or DottedKey. When providing both, they must refer to the same field definition, otherwise an error is thrown. | Integer |  | yes (if DottedKey not defined) |
| DottedKey | Dotted key of field definition that needs to be added to the profile. You can either provide FieldDefinitionId or DottedKey. When providing both, they must refer to the same field definition, otherwise an error is thrown. | String |  | yes (if FieldDefinitionId not defined) |
| ReadOnly | Is the field modifiable by the user? | Boolean | false | yes |
| Required | Should it be displayed as required | Boolean | false | no |
| Public | `Obsolete property, no longer has any effect. Use Scope instead.` | Boolean | true | no |
| Labels > Lang | The locale for the label. If not provided the translation of the field definition will be used | String |  | no |
| Labels > Value | The actual label for the given locale | String |  | no |
| Descriptions > Lang | The locale for the description. If not provided the translation of the field definition will be used | String |  | no |
| Descriptions > Value | The actual description for the given locale | String |  | no |
| Control | Indicates which control to use for profile field. This property accepts any string value. | String |  | no |

Note: `Public` property is obsolete and no longer has any effect. Property `Scope` can be used instead.

```json
{
  "FieldDefinitionId": 123,
  "DottedKey": "Dynamic.Label",
  "ReadOnly": false,
  "Required": false,
  "Labels": [
    {
      "Lang": "nl_BE",
      "Value": "Mijn label"
    }
  ],
  "Descriptions": [
    {
      "Lang": "nl_BE",
      "Value": "Mijn beschrijving"
    }
  ],
  "Control": "PersonsControl"
}
```

#### GenericList properties {#create_profile_field_genericlist_properties}

Properties only applicable for category `GenericList`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| DefaultVisible | Show a column by default or not in a generic list | Boolean | true | no | no |

```json
{
  "DefaultVisible": false
}
```

#### Facet properties {#create_profile_field_facet_properties}

Properties only applicable for category `Facet`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| SelectionType | The type of selection. `SHOULD`: at least one selected value must match. `MUST`: all selected values must match. | Enum | MUST | no | no |
| HideEmpty | Indicates if the empty facets are hidden. | Boolean | false | no | no |
| Sort | On what a facet is sorted. Possible values are `MostFrequent`, `Alphabetically`, `Chronologically`, `FixedOrder`. | Enum | depends on the field definition type | no | no |
| ReverseOrder | Sort the results in reverse order. Can only be true if Sort = `Chronologically`. | Boolean | false | no | no |
| DefaultNumberOfValues | The number of facets to show. Must be in range [1,100]. | Number | 10 | no | no |
| IncludeMissingValue | Include the missing value (e.g. `No Keywords`). | Boolean | true | no | no |
| IncludeActiveValues | Include values which are present as pure MUST terms in the query (e.g. `+Descriptive.Keywords.Keyword:Cork`). | Boolean | false | no | no |

Notes:
- The following rules apply to the Sort property:
- Values `MostFrequent` and `Alphabetically` are only applicable for non-date fields and non-enum fields, the default value is `MostFrequent`.
- Value `Chronologically` is only applicable for profile fields having a field definition with type `DateField`.
- Value `FixedOrder` is only applicable for profile fields having a field definition with type `EnumField`: values are sorted in the order in which the possible values are defined on the field definition.
- If SelectionType = `SHOULD`, the following applies: if a facet value is selected, this will affect the counts of all facets, except the facet itself. `SHOULD` is not applicable for date fields.

```json
{
  "SelectionType": "SHOULD",
  "HideEmpty": true,
  "Sort": "MostFrequent",
  "ReverseOrder": false,
  "DefaultNumberOfValues": 10,
  "IncludeMissingValue": false,
  "IncludeActiveValues": true
}
```

#### Classification properties {#create_profile_field_classification_properties}

Properties only applicable for category `Classification`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| Scope | The scope of the field. Possible values are `Public`, `Standard` and `Advanced`. Only allowed to be set on top fields. | Enum | Public (top fields) & null (non-top fields) | no | no |
| ChildrenToDisplay | List of child fields, specified by the key, to display in the user interface. Only allowed on fields of type MapField or MultiItemField. | List of strings | [] | no | no |

```json
{
  "Scope": "Standard",
  "ChildrenToDisplay": [
    "Author",
    "Artist"
  ]
}
```

Note: Since version `25.1` classification profiles allow both top and non-top fields.
Note: The property `Scope` is only allowed on top field and controls the permissions on a field:
- Reading a field with Scope = {SCOPE} requires the function VIEW_{SCOPE}_FIELDS (e.g. `VIEW_STANDARD_FIELDS`).
- Editing a field with Scope = {SCOPE} requires the function EDIT_{SCOPE}_FIELDS (e.g. `EDIT_STANDARD_FIELDS`).
- If a field is defined in different profiles with a different scope, the user must have at least one corresponding
  view / edit function in order to view / edit the field.

#### Ai properties {#create_profile_field_ai_properties}

Properties only applicable for category `Ai`:

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| GenerativeMetadata | Options about the generative metadata | [Generative metadata](#create_profile_field_ai_properties_generative_metadata) | null | no | no |
| Embedding | Options about the embedding | [Embedding](#create_profile_field_ai_properties_embedding) | null | no | no |

#### Ai properties: Generative metadata {#create_profile_field_ai_properties_generative_metadata}

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| Hint | Hint to give to the Ai for generating the value (if empty no value is generated) | String |  | no | no |
| IncludeInRequest | Include field as context for generative metadata | Boolean | False | no | no |
| MergeStrategy | Merge strategy for generative metadata if existing value is present (Keep, Overwrite, Merge) |  |  |  |  |
| MergeStrategy.Ingest | Merge strategy used when ingesting a new object | Enum | Depends on the field definition | no | no |
| MergeStrategy.Reharvest | Merge strategy used when reharvesting metadata for an object | Enum | Depends on the field definition | no | no |

Notes:
- The default MergeStrategy depends on the field definition:
- `Descriptive.Keywords.Keyword`: `Merge` for both `Ingest` and `Reharvest`
- `Descriptive.Title`: `Overwrite` for `Ingest`, `Keep` for `Reharvest`
- All other fields: `Keep` in both cases

#### Ai properties: Embedding {#create_profile_field_ai_properties_embedding}

| Property | Description | Type | Default Value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| Include | Include field in the semantic and similarity search context | Boolean | False | no | no |

```json
{
  "DottedKey": "Descriptive.Title",
  "GenerativeMetadata": {
    "Hint": "Generate a prosaic title",
    "IncludeInRequest": true,
    "MergeStrategy": {
      "Ingest": "Overwrite",
      "Reharvest": "Keep"
    }
  },
  "Embedding": {
    "Include": true
  }
}
```

## Linking Profiles and Top Records {#profiles}

Profiles can be linked with top records which is described in detail
on [Confluence](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/3273949212/Profiles).

### Getting profiles linked with record {#get-profiles-record}

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/profiles
```

Responds with a [record profiles object](#profiles-record-object).

Example:

```json
{
  "Profiles": [
    "04fe42a5-f6f3-483e-8e45-30a54b509c4d",
    "e6e678f5-a3e7-4e15-803e-406931b147ca"
  ],
  "RestrictedProfiles": [
    {
      "Id":  "b9f25e12-8e49-11eb-8dcd-0242ac130003",
      "RecordTypes":  ["Mh2Collection", "Record"]
    },
    {
      "Id":  "52276ed1-3759-427f-a2ce-406ecb24bec6",
      "RecordTypes":  ["Record"]
    }
  ]
}
```

### Setting the profiles linked with record {#set-profiles-record}

Requires the function `ADMIN_PROFILES`

```http
PUT https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/profiles
```

With a [record profiles object](#profiles-record-object) in JSON

Example:

```json
{
  "Profiles": [
    "04fe42a5-f6f3-483e-8e45-30a54b509c4d",
    "e6e678f5-a3e7-4e15-803e-406931b147ca"
  ],
  "RestrictedProfiles": [
    {
      "Id":  "b9f25e12-8e49-11eb-8dcd-0242ac130003",
      "RecordTypes":  ["Mh2Collection", "Record"]
    }
  ]
}
```

#### Response

- `204` No content
- `400` The same profile ID appears both in `Profiles` and `RestrictedProfiles`
- `404` The record or one of the profiles was not found.

### Record profiles object {#profiles-record-object}

The property `Profiles` are profiles linked with the top record for the record types configured on the profile itself.
`RestrictedProfiles` are profiles linked with the top record with a different set of record types than configured for
the `Profile` itself. See property [Profile.RecordTypes](#profile_object).

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Profiles | String[] (UUID) | Array of IDs of profiles to link | [] |  |
| RestrictedProfiles | RestrictedProfile[] | Array of restricted profiles to link | [] |

### Restricted Profiles {#profiles-restricted-profile}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Id | String (UUID) | Id of the profile to link |  | yes |
| RecordTypes | String[] | Array of `RecordType` for which the profile applies. An empty array means `All` record types. | [] | no |

## Classifications and metadata profiles {#classifications}

[Classifications](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/4514578529/Classifications)
are records at the top of the record tree that can be linked
with [Profiles](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/4195483661/Metadata+Classification+Profiles).

### Getting classifications {#classifications-get-all}

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/classifications
```

Returns all published classifications

In addition to the standard [Page parameters](#page-filter) the following
parameters are available:

| Query parameter | Type | Description | Default Value |
| --- | --- | --- | --- |
| published | Boolean | Whether to return only published classifications. | False |
| q | String | Free text search string that supports [query syntax](#query-syntax). |  |
| organisationId | Integer | The ID of the [organisation](#organisations). Requires the function `ADMIN_VIEW_ALL_ORGANISATIONS` for an organisation different from the user | < organisation ID of the user > |

#### Response

- `200` Ok. [page](#page) of [classification records](#record-object)
- `400` Invalid query `q`
- `403` User has no access to the organisation

### Get a single classification {#classification-get-one}

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/classifications/:recordId
```

Knowledge of the record ID is sufficient to access it.

#### Response

- `200` Ok. [Classification record](#record-object)
- `400` Invalid record ID
- `404` Classification does not exist

### Getting profiles linked with classification {#classifications-get-profiles}

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/classifications/:recordId/profiles
```

Knowledge of the record ID is sufficient to access it.

#### Response

- `200` Ok. [Classification profiles object](#classifications-record-object)
- `400` Invalid record ID
- `404` Classification does not exist

#### Example

```json
{
  "Profiles": [
    "04fe42a5-f6f3-483e-8e45-30a54b509c4d",
    "e6e678f5-a3e7-4e15-803e-406931b147ca"
  ]
}
```

### Business rules for modifying classifications {#classifications-functions}

- The function `ADMIN_PROFILES` is required
- The specified profiles can only be used for 1 classification
- The specified profiles must either be shared (organisation is NULL) or have the same organisation as the
  classification
- When the classification is from another organisation than the user, the function `ADMIN_EDIT_ALL_ORGANISATIONS` is
  required.

### Setting the profiles of a classification {#classifications-profiles-set}

```http
PUT https://archief.viaa.be/mediahaven-rest-api/v2/classifications/:recordId/profiles
```

With as body a [classifications profiles object](#classifications-record-object)

#### Example

```json
{
  "Profiles": [
    "04fe42a5-f6f3-483e-8e45-30a54b509c4d",
    "e6e678f5-a3e7-4e15-803e-406931b147ca"
  ]
}
```

#### Response

- `204` No content
- `400` Invalid profile ID
- `400` At least 1 profile is not a classification
- `403` At least 1 profile belongs to a different organisation than the classification
- `404` The classification or one of the profiles were not found.
- `409` At least 1 profile is already linked with another classification
- `423` Changes are already being retroactively applied to this classification

### Create a profile of a classification {#classifications-profiles-create}

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/classifications/:recordId/profiles
```

With as body a [create classifications profile](#create_profile_object) whose `Category` MUST BE `Classification`.

#### Example

```json
{
  "Name": "Mijn metadata profiel",
  "Names": [
    {
      "Lang": "en_US",
      "Value": "My metadata profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn metadata profiel"
    }
  ],
  "OrganisationId": 178,
  "RecordTypes": [
    "Media"
  ],
  "Description": "Mijn mooi profiel",
  "Descriptions": [
    {
      "Lang": "en_US",
      "Value": "My beautiful profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn mooi profiel"
    }
  ],
  "Fields": [
    "<Profile field>"
  ]
}
```

#### Response

- `201` The created [Profile](#profile_object)
- `400` The request is not valid
- `400` Profile is not a classification
- `403` Profile belongs to a different organisation than the classification
- `403` User does not have the correct [functions](#classifications-functions)
- `404` Classification does not exist
- `423` Changes are already being retroactively applied to this classification

### Update a profile of a classification {#classifications-profiles-update}

```http
PUT https://archief.viaa.be/mediahaven-rest-api/v2/classifications/:recordId/profiles/:profileId
```

With as body a [classifications profile](#profile_object) whose `Category` MUST BE `Classification`.

#### Example

```json
{
  "Name": "Mijn metadata profiel",
  "Names": [
    {
      "Lang": "en_US",
      "Value": "My metadata profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn metadata profiel"
    }
  ],
  "OrganisationId": 178,
  "RecordTypes": [
    "Media"
  ],
  "Description": "Mijn mooi profiel",
  "Descriptions": [
    {
      "Lang": "en_US",
      "Value": "My beautiful profile"
    },
    {
      "Lang": "nl_BE",
      "Value": "Mijn mooi profiel"
    }
  ],
  "Fields": [
    "<Profile field>"
  ]
}
```

#### Response

- `204` The profile was updated
- `400` The request is not valid
- `403` User does not have the correct [functions](#classifications-functions)
- `404` The profile or classification could not be found
- `423` Changes are already being retroactively applied to this classification

### Delete a profile of a classification {#classifications-profiles-delete}

```http
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/classifications/:recordId/profiles/:profileId
```

#### Response

- `204` The profile was deleted
- `400` Invalid classification ID or profile ID
- `400` The profile is not a classification
- `400` The profile does not belong to the classification
- `400` The request is not valid
- `403` User does not have the correct [functions](#classifications-functions)
- `404` The profile or classification could not be found
- `423` Changes are already being retroactively applied to this classification

### Publish changes to a classification and its profiles {#classifications-publish-changes}

After changing or reordering which profiles are linked with classification or changing the record types
of the profiles, these changes need to be published and retroactively applied to existing records under the
classification. Note that these particular changes also do *not* to apply new records under the classification
until they are explicitly published using this method.
All changes to specific profiles (i.e. new fields, changing existing fields, setting a field required, etc.),
apart from the record types of the profile instantly apply and cannot be published.

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/classifications/:recordId/publish-changes
```

This method starts a [batch](#batches) whose progress that can be tracked.
As long as this batch is active, the classification or its profiles are read-only.

#### Response

- `201` The [Classifications publish-changes object](#classifications-publish-changes-object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct [functions](#classifications-functions)
- `404` The classification could not be found
- `423` Changes are already being retroactively applied to this classification

### Classifications metadata {#classifications-metadata}

Classifications have the following metadata fields to track their status

| Dotted Key | Type | Description | Default |
| --- | --- | --- | --- |
| `RecordInformation.Classification.BatchId` | String (UUID) | Stores the most recent batch linked with this classification |  |
| `RecordInformation.Classification.HasChanges` | Boolean | Whether there pending changes that must be retroactively applied | false |

The batch completion step changes the value to false |

### Classifications profiles object {#classifications-record-object}

The property `Profiles` are profiles linked with the classification for the record types configured on the profile
itself.

| Property | Type | Description |
| --- | --- | --- |
| Profiles | String[] (UUID) | Array of IDs of profiles to link |

### Classifications publish-changes object {#classifications-publish-changes-object}

| Property | Type | Description |
| --- | --- | --- |
| BatchId | String (UUID) | Batch ID of the created batch |

## Metadata translations {#metadata_translations}

### Description {#metadata_translations_description}

With this endpoint you can configure metadata translations which are a mapping of field definitions
to technical keys that can be “burned” into a file during export. An [export location](#export_locations) can then be
configured to use this mapping. Examples of technical keys that can be burned are for example `XMP_title`.
Operating systems such as Windows for example display a subset of these technical keys in context menus for files.

### Translation {#metadata_translations_translation}

When translating a metadata field into the value to be burned in, the following rules are applied
*For simple fields, the value is its string value* For complex fields, the value is the string concatenation of all (grand)child simple fields, joined by the configured
separator of the translation

Modifying the mapping, namely specifying the list of field definitions and their associated technical key
is done by changing the profile that is created during the creation of the metadata translation using the existing
[profile API](#profiles_field_create).

### Translation keys {#metadata_translations_get_keys}

To obtain the possible translation keys use a `GET` request:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/metadata-translations/keys
```

It returns a JSON object with as key the family of translations and as value a JSON array of possible keys for this
family.

```json
{
    "XMP": ["XMP_title", ...],
    "EXIF: ["EXIF_ModifyDate", ...]
}
```

### Get all translations {#metadata_translations_get_all}

Retrieve [Metadata translations](#metadata_translations_object) using a `GET` request:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/metadata-translations
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Only return metadata translations from this organisation |  |
| sort | Sort on one of the following fields: Name, OrganisationId,CreationDate, LastModifiedDate | Name |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

#### Response

- `200` A [Page](#page) of [Metadata translations](#metadata_translations_object)
- `403` The user does not have the required functions to call this method or has no access to this organisation

#### Authorization functions

- Using this endpoint requires no special functions
- Requesting metadata translations from organisation different of the current user, requires
  the `ADMIN_VIEW_ALL_ORGANISATIONS` function

### Get a specific translation {#metadata_translations_get}

Retrieve a specific [Metadata translation](#metadata_translations_object) using a `GET` request:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/metadata-translations/:id
```

#### Response

- `200` A [Metadata translation](#metadata_translations_object)
- `403` The user does not have access to the translation
- `404` The translation does not exist

#### Authorization functions

- Using this endpoint requires no special functions apart from being member of the organisation of the translation
- Requesting metadata translations from an organisation different of the current user, requires
  the `ADMIN_VIEW_ALL_ORGANISATIONS` function

### Metadata translations object {#metadata_translations_object}

| Property | Type | Description |
| --- | --- | --- |
| Id | UuidV4 | The unique identifier of the translation |
| Name | String | The name of the translation, unique for the organisation |
| Separator | String | The seperator to use when joining values |
| OrganisationId | Number | ID of the organisation it belongs to |
| ProfileId | UuidV4 | ID of the [profile](#profiles) linked with this translation. Automatically created. |
| CreationDate | Date (ISO8601) | Date when the translation was created |
| LastModifiedDate | Date (ISO8601) | Date when the translation was last modified |

### Create a new translation {#metadata_translations_post}

Create a new [Metadata translations](#metadata_translations_object) using a `POST` request
with [body](#metadata_translations_object_post).

```http
https://archief.viaa.be/mediahaven-rest-api/v2/metadata-translations
```

#### Response

- `200` A new [Metadata translation](#metadata_translations_object)
- `400` Invalid name or separator
- `403` User does not have the function `ADMIN_METADATA_TRANSLATION`
- `403` User has no access to the specified organisation
- `404` Specified organisation does not exist
- `409` Name already exists for the organisation

#### Authorization functions

- Using this endpoint requires the function `ADMIN_METADATA_TRANSLATION`
- Creating metadata translations from an organisation different of the current user, requires
  the `ADMIN_EDIT_ALL_ORGANISATIONS` function

### Updating an existing translation {#metadata_translations_put}

Update an existing [Metadata translation](#metadata_translations_object) using a `PUT` request
with [body](#metadata_translations_object_put).

```http
https://archief.viaa.be/mediahaven-rest-api/v2/metadata-translations/:id
```

#### Response

- `200` The updated [Metadata translation](#metadata_translations_object)
- `400` Invalid name or separator
- `403` User does not have the function `ADMIN_METADATA_TRANSLATION`
- `403` User has no access to the metadata translation
- `404` Metadata translation does not exist
- `409` Name already exists for the organisation

#### Authorization functions

- Using this endpoint requires the function `ADMIN_METADATA_TRANSLATION`
- Creating metadata translations from an organisation different of the current user, requires
  the `ADMIN_EDIT_ALL_ORGANISATIONS` function

### Create metadata translation object {#metadata_translations_object_post}

| Property | Type | Description | Default |
| --- | --- | --- | --- |
| Name | String | The name of the translation, unique for the organisation | *required* |
| OrganisationId | Number | ID of the organisation it belongs to | *organisation of the user* |
| Separator | String | The separator to use when joining values | , |

### Update metadata translation object {#metadata_translations_object_put}

| Property | Type | Description | Default |
| --- | --- | --- | --- |
| Name | String | The name of the translation, unique for the organisation | *required* |
| Separator | String | The separator to use when joining values | , |

## Notifications {#notifications}

Notifications are a concept to notify users with messages which are distinct from events.

- Notifications are sent to functions or groups
- Notifications are cleared after a number of days
- Notifications are read by individual users

### Required functions {#notifications_functions}

For sending notifications the user requires the `SEND_NOTIFICATIONS` function to post to this endpoint. Notifications
are only sent to users within the same organisation as the sender.

### Notification object structure {#notifications_datamodel}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Id | String (UUID) | A unique notification id. | yes |  |  |
| Title | String | Title of the notification |  |  | yes |
| Body | String | Description of the notification |  |  |  |
| Action | String | URI to an item the notification is about |  |  |  |
| Tag | String | Classification of the notification which can be specified when getting |  |  |  |
| New | Boolean | Whether the notification is new for the user. This is set to true initially, and stays this way until marked as seen. | yes | true |  |
| SentOn | Date (ISO8601) | Date on which the message was sent. | yes | The current date |  |
| RecordId | String | The RecordId (former MediaObjectId) of the record associated with the notification. |  |  |

Example:

```json
{
  "Id": "73db6850-02bb-40bd-9722-ca6fb64115b4",
  "Title": "Record gepubliceerd.",
  "Body": "Het record dat je hebt opgeladen is gearchiveerd.",
  "Action": "2b9661bad98f481aaebafed66f4260a80835f90b7e994cd49e83ab530c70332f",
  "Tag": "record.published",
  "SentOn": "2021-03-23T14:25:08.278000Z",
  "New": true,
  "RecordId": "2b9661bad98f481aaebafed66f4260a80835f90b7e994cd49e83ab530c70332f"
}
```

### Create notification {#create_notification}

To create a new notification you can send a `POST` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/notifications/
```

The endpoint supports json with the following properties

#### Create notification object structure {#create_notifications_datamodel}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Notification | [Notification](#notifications_datamodel) |  |  |  | yes |
| Function | String | Send to the users of your organisation with this function |  |  | yes (see note) |
| Group | String | Send to users who are member of this group |  |  | yes (see note) |

> Note: either Function or Group must be specified.

Example request body:

```json
{
  "Notification": {
    "Title": "test",
    "Body": "test",
    "Action": "http://example.come",
    "Tag": "EXAMPLE.TEST",
    "RecordId": "ea69377fe3024929a5bb7323eb873498ec8c4820975a4694b0db556e6384312f"
  },
  "Function": "access_management_module"
}
```

#### Response

- `204` Created.
- `400` Bad request
- `403` User is not authorized

### Listing all notifications {#get_all_notifications}

The notifications can be retrieved using a `GET` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/notifications
```

This will return a list of the notifications in a paginated format. Page navigation is similar as for [navigating search result pages](#basic-searching), by using the following query parameters:

| Query parameter | Description | Default |
| --- | --- | --- |
| tag | Filter on a specific tag |  |
| tagPrefix | Filter on a specific tag prefix |  |
| onlyNew | Show only new notifications | false |
| nrOfResults | Number of results per page | 25 |
| startIndex | Index of result where to start | 0 |
| sort | Sort on one of the following fields (SentOn, Body, Title, ReadOn) | SentOn |
| direction | The direction can be `asc`, `up`, `desc` or `down` | desc |

Example response

```json
{
  "NrOfResults": 1,
  "StartIndex": 0,
  "TotalNrOfResults": 8,
  "Results": [
    {
      "Id": "73db6850-02bb-40bd-9722-ca6fb64115b4",
      "Title": "Record gepubliceerd.",
      "Body": "Het record dat je hebt opgeladen is gearchiveerd.",
      "Action": "2b9661bad98f481aaebafed66f4260a80835f90b7e994cd49e83ab530c70332f",
      "Tag": "record.published",
      "SentOn": "2021-03-23T14:25:08.278000Z",
      "New": true,
      "RecordId": "2b9661bad98f481aaebafed66f4260a80835f90b7e994cd49e83ab530c70332f"
    }
  ]
}
```

#### Response

- `200` Ok. A list of [Notifications](#notifications_datamodel)
- `400` Query parameters could not be parsed
- `403` User is not authorized

### Get number of notifications {#get_notifications_count}

The get the total number of notifications match your query, do a `HEAD` call to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/notifications
```

The request also accepts the following query parameters:

| Query parameter | Description | Default |
| --- | --- | --- |
| tag | Filter on a specific tag |  |
| tagPrefix | Filter on a specific tag prefix |  |
| onlyNew | count only new notifications | false |

The response will contain a header element with the name `Result-Count`.

#### Response

- `200` Ok.
- `400` Query parameters could not be parsed
- `403` User is not authorized

### Mark notifications as outdated {#mark_notifications_not_new}

To mark all notifications of the current user as not new, do a `POST` request to

```http
https://archief.viaa.be/mediahaven-rest-api/v2/notifications/mark-as-outdated
```

You can provide a request body with a request body with a date parameter ‘SentBefore’.
Only the notifications that were sent before this time will be marked as outdated.

```json
{
  "SentBefore": "<Date ISO8601>"
}
```

#### Response

- `200` Notifications have been marked as outdated
- `400` Incorrect date format
- `403` User is not authorized

### Deleting a notification {#delete_notification}

To delete a notification you have to send a `DELETE` call to the following endpoint

```http
https://archief.viaa.be/mediahaven-rest-api/v2/notifications/:id
```

This will return a response with status code 204 if successful

### Deleting multiple notifications {#delete_notifications}

To delete multiple notifications you have to send a `DELETE` call to the following endpoint:

```http
 https://archief.viaa.be/mediahaven-rest-api/v2/notifications
```

With as body a JSON Array of notification IDs. Unknown or already deleted notifications IDs are silently ignored.

Example request body

```json
["f50aa13e-d1b1-4481-ba87-e07a3c8940c5", "b22bf79b-493b-477c-bf2b-f7d847179c7a"]
```

When providing no body or an empty JSON Array all notifications of the user will be deleted:

```json
[]
```

#### Response

- `204` Notifications have been deleted
- `400` One or more invalid UUIDs were provided
- `403` User is not authorized

## Webhooks {#webhooks}

Webhooks in MediaHaven are user defined HTTP callbacks which are triggered when an event happens. Depending on the user’s functions, webhooks can return two types of events:
- Premis events: Webhooks return premis events of records to which the user has read access. The event name always start with prefix `RECORDS`.
- Audit events: If the user has the function `ADMIN_EDIT_ALL_ORGANISATIONS`, audit events from other concepts (users, organisations, …) are also included.

Interaction with the webhooks endpoint is only allowed for users with the `REGISTER_WEBHOOKS` function. Below is
explained how you to create, list, get and delete webhooks.

Webhooks are always linked to a user. So all endpoints return webhooks linked to the currently authenticated user.

### Creating a webhook {#webhook_creating}

A webhook can be created by performing a `POST` request with [Webhook](#webhook_object) as body to:

```http
POST https://archief.viaa.be/mediahaven-rest-api/v2/webhooks
```

#### Response

- `201` The created [Webhook](#webhook_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function
- `409` The url is already defined as webhook for the current user.

#### Authorization functions

- Using this endpoint requires the `REGISTER_WEBHOOKS` function.

### List all webhooks {#webhook_list}

To get a list of all webhooks you have created, make a `GET` request to:

```http
GET https://archief.viaa.be/mediahaven-rest-api/v2/webhooks
```

#### Response

- `200` A list of all [Webhooks](#webhook_object) linked to the current user

#### Authorization functions

- Using this endpoint requires the `REGISTER_WEBHOOKS` function.

### Get a specific webhook {#webhook_get}

A single webhook can be fetched by performing a `GET` request to:

```http
 GET https://archief.viaa.be/mediahaven-rest-api/v2/webhooks/:webhookId
```

Only webhooks created by the current user can be accessed.

#### Response

- `200` Single [Webhook](#webhook_object)
- `400` Webhook id is not valid
- `403` User has no access to the webhook
- `404` The webhook could not be found

#### Authorization functions

- Using this endpoint requires the `REGISTER_WEBHOOKS` function.

### Updating a webhook {#webhook_update}

A webhook can be updated by performing a `PUT` request to:

```http
PUT https://archief.viaa.be/mediahaven-rest-api/v2/webhooks/:webhookId
```

#### Response

- `201` The updated [Webhook](#webhook_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function
- `409` The url is already defined as webhook for the current user.

#### Authorization functions

- Using this endpoint requires the `REGISTER_WEBHOOKS` function.

### Deleting a webhook {#webhook_delete}

To delete a webhook, make a `DELETE` request to:

```http
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/webhooks/:webhookId
```

You must be the owner of the webhook to be able to delete it.

#### Response

- `204` The webhook is deleted
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function
- `404` The webhook does not exist

#### Authorization functions

- Using this endpoint requires the `REGISTER_WEBHOOKS` function.

### Receiving a webhook message {#webhook_message}

When you receive a webhook event it will follow the following XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<events>
    <premis:event xmlns:premis="info:lc/xmlns/premis-v2">
        <premis:eventIdentifier>
            <premis:eventIdentifierType>MEDIAHAVEN_EVENT</premis:eventIdentifierType>
            <premis:eventIdentifierValue>4940161</premis:eventIdentifierValue>
        </premis:eventIdentifier>
        <premis:eventType>EXPORT</premis:eventType>
        <premis:eventDateTime>2019-03-30T05:28:40Z</premis:eventDateTime>
        <premis:eventDetail>Because I'm such a nice guy</premis:eventDetail>
        <premis:eventOutcomeInformation>
            <premis:eventOutcome>OK</premis:eventOutcome>
        </premis:eventOutcomeInformation>
        <premis:linkingAgentIdentifier>
            <premis:linkingAgentIdentifierType>MEDIAHAVEN_USER</premis:linkingAgentIdentifierType>
            <premis:linkingAgentIdentifierValue>703a53d2-dc66-4eb2-ab7f-73d5fd228852
            </premis:linkingAgentIdentifierValue>
        </premis:linkingAgentIdentifier>
        <premis:linkingObjectIdentifier>
            <premis:linkingObjectIdentifierType>MEDIAHAVEN_ID</premis:linkingObjectIdentifierType>
            <premis:linkingObjectIdentifierValue>
                1d47c9ebcf364907a60838a0627693f6136574c2f4034ba3b662ed17889ec825cafdce6634b84b71ab4c82a8aa777164
            </premis:linkingObjectIdentifierValue>
        </premis:linkingObjectIdentifier>
        <premis:linkingObjectIdentifier>
            <premis:linkingObjectIdentifierType>EXTERNAL_ID</premis:linkingObjectIdentifierType>
            <premis:linkingObjectIdentifierValue>9815587</premis:linkingObjectIdentifierValue>
        </premis:linkingObjectIdentifier>
    </premis:event>
</events>
```

### Webhook object structure {#webhook_object}

| Property | Type | Description | ReadOnly | Default Value | Required |
| --- | --- | --- | --- | --- | --- |
| Id | String (UUID) | The unique identifier of this webhook | Yes |  |  |
| Url | String (URL) | The url you want to receive the events on |  |  | Yes |
| CreationDate | Date (ISO8601) | The date the webhook was created | Yes |  |  |
| Format | String | The format of the premis event. Possible values are `Xml`, `XmlPremisV3` |  | Xml |  |
| Filter.RecordTypes | String[] | Filter to subscribe only to specific record types. Wildcard \* at the end of a value is allowed. |  | empty list (all types) |  |
| Filter.EventTypes | String[] | Filter to subscribe only to specific event types. Wildcard \* at the end of a value is allowed. |  | empty list (all types) |

Notes:
- When using the format `XmlPremisV3` the event is outputted using Premis version 3 and includes the
  [difference](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/4058742786/Difference) for events
  that changed the metadata.
- The url has to meet the following criteria:
- must be accessible from the internet
- must use HTTPS scheme
- must be a valid url
- no existing webhook may be linked to this url for the authenticated user
- `Filter.RecordTypes` only applies to events starting with type `RECORDS`.

```json
{
  "Id": "a97a0b05-ad98-48ef-b072-969c2a5b0c7e",
  "Url": "https://webhook.site/9ca0cfd3-5948-447d-8c43-38971c4c6efd",
  "CreationDate": "2021-06-03T14:52:24.889000Z",
  "Format": "Xml",
  "Filter": {
    "RecordTypes: ["Record", "Media", "Media.*"],
    "EventTypes": ["RECORDS.UPDATE", "RECORDS.UPDATE.*", "USERS.FLOW.*"]
  }
}
```

## Organisations {#organisations}

### Listing organisations {#listing_organisations}

Retrieve a [Page](#page) of [Organisations](#organisation-object) using a `GET` request

```http
https://archief.viaa.be/mediahaven-rest-api/v2/organisations
```

The standard [Page parameters](#page-filter) are available.

#### Response

- `200` A [Page](#page) of [Organisations](#organisation-object)

#### Authorization functions

- Using this endpoint requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Getting an organisation {#fetching_organisation}

A single organisation can be fetched by performing a `GET` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id
```

#### Response

- `200` Ok. Body: [Organisation](#organisation-object)
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Getting an organisation by ExternalId {#fetching_organisation_externalid}

An organisation can be fetched by its ExternalId performing a `GET` request to:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:ExternalId
```

#### Response

- `200` Ok. Body: [Organisation](#organisation-object)
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve all default roles for an organisation {#listing_organisation_defaults_roles}

In order to get a complete list of all roles assigned to newly created users (internal and external authentication) for an organisation, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/roles
```

See the section on [Roles](#roles) for more information.

#### Response

- `200` Ok. [Page](#page) of [Roles](#roles_datamodel)
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve all default functions for an organisation {#listing_organisation_defaults_functions}

In order to get a complete list of all functions assigned to newly created users (internal and external authentication) for an organisation, do a `GET` request to the following endpoint:

```http
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/functions
```

#### Response

- `200` Ok. An array containing all functions assigned to newly created users.

  ```json
  [
  "<string>"
  ]
  ```
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve all default zones for an organisation {#listing_organisation_defaults_zones}

In order to get a complete list of all zones assigned to newly created users (internal and external authentication) for an organisation, do a `GET` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/zones
```

See the section on [zones](#zones) for more information.

#### Response

- `200` Ok. [Page](#page) of [Zones](#zone_datamodel)
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve all default preferences for an organisation {#listing_organisation_defaults_preferences}

In order to retrieve all preferences assigned to newly created users (internal and external authentication) for an organisation, do a `GET` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/preferences
```

#### Response

- `200` Ok. Body: [User preferences](#user_preferences_object)
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve all default groups for an organisation {#listing_organisation_defaults_groups}

In order to get a complete list of all groups assigned to newly created users (internal and external authentication) for an organisation, do a `GET` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/groups
```

See the section on [groups](#groups) for more information.

#### Response

- `200` Ok. [Page](#page) of [Groups](#group_datamodel)
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve all default global rights for an organisation {#listing_organisation_defaults_rights}

In order to retrieve all global rights (read, write, export, delete) assigned to newly created users (internal and external authentication) for an organisation, do a `GET` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/rights
```

#### Response

- `200` Ok. Body: [User rights](#user_rights_object)
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Retrieve default locale for an organisation {#fetching_organisation_defaults_locale}

In order to retrieve the default locale assigned to newly created users (internal and external authentication) for an organisation, do a `GET` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/locale
```

#### Response

- `200` Ok. The default locale in plain text format.
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Update an organisation {#update_organisation}

Updating an organisation can be done by performing a PUT-request with [Organisation](#organisation-object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id
```

#### Response

- `200` Ok. Body: Updated [organisation](#organisation-object)
- `403` No access to the organisation in question.
- `400` One or more of the provided property values were not valid.

#### Authorization functions

- Updating your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating any other organisation requires the function `ADMIN_ORGANISATION` and `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Update default roles for an organisation {#update_organisation_defaults_roles}

Default roles can be updated by performing a PUT-request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/roles
```

with an array of role ids:
```
[
  "<uuid of role>",
  ...
]
```

#### Response

- `204` Roles were updated.
- `403` No access to the organisation or missing functions.
- `404` The organisation does not exist or one or more of the role ids do not exist.

#### Authorization functions

- Updating the defaults of your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating the defaults of any other organisation requires the function `ADMIN_ORGANISATION` and
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Update default functions for an organisation {#update_organisation_defaults_functions}

Default functions can be updated by performing a PUT-request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/functions
```

with an array of function names:
```
[
  "<string>",
  ...
]
```

#### Response

- `204` The list of functions was updated.
- `403` No access to the organisation in question.
- `404` The organisation does not exist or one or more of the functions do not exist.

#### Authorization functions

- Updating the defaults of your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating the defaults of any other organisation requires the function `ADMIN_ORGANISATION` and
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Update default zones for an organisation {#update_organisation_defaults_zones}

Default zones can be updated by performing a PUT-request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/zones
```

with an array of zone ids:
```
[
  "<uuid of zone>",
  ...
]
```

#### Response

- `204` Zones were updated.
- `403` No access to the organisation or one or more of the zones in question.
- `404` The organisation does not exist or one or more of the zone ids do not exist.

#### Authorization functions

- Updating the defaults of your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating the defaults of any other organisation requires the function `ADMIN_ORGANISATION` and
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Update default preferences for an organisation {#update_organisation_defaults_preferences}

Default preferences can be updated by performing a PUT-request with [User preferences](#user_preferences_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/preferences
```

Preferences that are not explicitly defined in the request will not be changed.

#### Response

- `200` Ok. Body: [User preferences](#user_preferences_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the organisation in question.
- `404` The organisation does not exist or one or more of the provided property values (ids) do not exist or the organisation does not have access to them.

#### Authorization functions

- Updating the defaults of your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating the defaults of any other organisation requires the function `ADMIN_ORGANISATION` and
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Update default groups for an organisation {#update_organisation_defaults_zones}

Default groups can be updated by performing a PUT-request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/groups
```

with an array of groups ids:
```
[
  "<uuid of group>",
  ...
]
```

#### Response

- `204` Groups were updated.
- `403` No access to the organisation or one or more of the groups in question.
- `404` The organisation does not exist or one or more of the group ids do not exist.

#### Authorization functions

- Updating the defaults of your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating the defaults of any other organisation requires the function `ADMIN_ORGANISATION` and
  `ADMIN_EDIT_ALL_ORGANISATIONS`.
- Adding default groups from a different organisation than the organisation itself requires the function
  `ADMIN_EDIT_ALL_ORGANISATIONS` or `ADMIN_EXTERNAL_USERS` (legacy).

### Update default global rights for an organisation {#update_organisation_defaults_preferences}

Default global rights (read, write, export, delete) can be updated by performing a PUT-request with [User rights](#user_rights_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/rights
```

Global rights that are not explicitly defined in the request will not be changed.

#### Response

- `200` Ok. Body: [User rights](#user_rights_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Updating the defaults of your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating the defaults of any other organisation requires the function `ADMIN_ORGANISATION` and
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Update default locale for an organisation {#update_organisation_defaults_locale}

The default locale can be updated by performing a PUT-request with the locale value as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/defaults/locale
```

Possible values can be retrieved via the [Locales](#locales) endpoint.

#### Response

- `200` Locale was updated.
- `400` Locale was not valid.
- `403` No access to the organisation in question.
- `404` The organisation does not exist.

#### Authorization functions

- Updating the defaults of your own organisation requires the function `ADMIN_ORGANISATION`.
- Updating the defaults of any other organisation requires the function `ADMIN_ORGANISATION` and
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Creating a new organisation {#create_organisation}

Creating a new organisation can be done by performing a `POST`-request with [Create organisation object](#create-organisation-object) in the body to the endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/
```

`Note:` Unlike other create endpoints, if there’s already an organisation with the provided name the existing organisation will be updated.

#### Response

- `202` Organisation will be created.
- `400` Organisation was not valid.
- `403` The current user does not have the correct permissions to create an organisation.

#### Authorization functions

- Creating a new organisation requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Creating new organisations in bulk {#create_organisation_bulk}

Creating a new organisation can be done by performing a `POST`-request to the endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/actions
```

The body looks like this:
```
{
    "Type": "BULK_CREATE",
    "Data": [
      {
        "Name": "gent",
        "LongName": "Gemeente Gent",
        "ExternalId": "OVO001834",
        "Domain": "gent.mediahaven.be",
        "Locale": "nl_BE"
      },
      {
        "Name": "roeselare",
        "LongName": "Gemeente Roeselare",
        "Domain": "roeselare.mediahaven.be",
        "Locale": "nl_BE"
      }
    ] 
}
```

See [Create organisation object](#create-organisation-object) for all available options for the creation of an organisation.

`Note:` If one or more of the organisations have a name that already exists, the existing organisation will be updated.

#### Response

- `202` The request was accepted.
- `400` One or more organisations are not valid.
- `403` The current user does not have the correct permissions to create an organisation.
- `409` A create is already in progress

#### Authorization functions

- Creating a new organisation requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Getting the modules of an organisation {#organisation_list_modules}

To list all modules linked to an organisation, do a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/:id/modules
```

The standard [Page parameters](#page-filter) are available.

#### Authorization functions

- Any authenticated user can access their own organisation.
- Accessing any other organisation requires at least one of the following functions: `ADMIN_VIEW_ALL_ORGANISATIONS`,
  `ADMIN_EDIT_ALL_ORGANISATIONS`.

#### Response

- `200` A [Page](#page) of [Modules](#module-object)
- `400` The request is not valid
- `401` User is not authorized
- `403` The user does not have access to the organisation
- `404` The organisation does not exist

### Organisation object structure {#organisation-object}

| Property | Type | Description | Readonly | Required |
| --- | --- | --- | --- | --- |
| Id | Number | A unique id. | Yes |  |
| Name | String | The (short) organisation name. | Yes |  |
| LongName | String | The (full) organisation name. | No | Yes |
| CustomProperties | JsonObject | Custom properties for the organisation. | No | No |
| TenantGroup | String | Property which groups a number of organisations together (DigiHaven only). | Yes |  |
| ExternalId | String | The external id of the organisation, must be unique | No | No |
| EnginePlugins | Array of strings | `Deprecated property, might be removed in the future.` The engine plugins activated for this organisation. | No | No |

Example:
```
{
  "Id": 104,
  "Name": "gent",
  "LongName": "Gemeente Gent",
  "ExternalId": "OVO001834",
  "CustomProperties": {
    "MyProperty": "myValue",
    "MyComplexProperty": {
      "MaxCount": 3,
      "MinCount": 1
    }
  },
  "TenantGroup": null
}
```

## User rights object structure {#user_rights_object}

| Property | Description |
| --- | --- |
| ReadRights | Does the user have read right. |
| WriteRights | Does the user have write right. Can only be set to true if ReadRights is set to true. |
| DeleteRights | Does the user have delete right. Can only be set to true if ReadRights is set to true. |
| ExportRights | Does the user have export right. Can only be set to true if ReadRights is set to true. |

Example:
```
{
  "ReadRights": true,
  "WriteRights": true,
  "DeleteRights": false,
  "ExportRights": true
}
```

### Create organisation object structure {#create-organisation-object}

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| Name | String | The (short) organisation name. | Yes |  |
| LongName | String | The (full) organisation name. If not provided, will be set to Name. | No | Value of name |
| ExternalId | String | The external id of the organisation, must be unique | No |  |
| Domain | String | Domain of the customer/organisation | Yes |  |
| DomainShared | Boolean | Whether the domain of the customer/organisation is shared with other organisations | No | False |
| Locale | String | The default locale of the organisation | No | nl_BE |
| MobPublic | boolean | If the main original storage mob pool is available publicly | No | False |
| BackupPools | boolean | Whether to add backup pools | No | True |
| OverwritePretranscoderConfig | boolean | Whether to overwrite the existing pretranscoder config | No | False |
| PluginParameters | Json object | The parameters to pass to the activate organisation plugins. | No |  |
| RecordSchemeRef | String | Reference to an existing record scheme (monitor,media,digihaven_in_mediahaven) | No |  |
| EnginePlugins | Array of strings | `Obsolete property, has no longer any effect.` The engine plugins that will be activated for this organisation. | No | Empty array |
| AdditionalPlugins | Array of strings | Additional add-organisation plugins to activate for this specific customer/organisation after the global plugins | No |

Notes:
- Which EnginePlugins are active depends on which [module plugins](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/4438884395/Module+Plugins) with category = `ActionModel` are active for an organisation.

Example:
```
{
  "Name": "gent",
  "LongName": "Gemeente Gent",
  "ExternalId": "OVO001834",
  "Domain": "gent.mediahaven.be",
  "Locale": "nl_BE",
  "MobPublic": false,
  "DomainShared": false,
  "BackupPools": true,
  "OverwritePretranscoderConfig": false,
  "PluginParameters": {
    "ApplicationScope": "gemeentes",
    "IsDigitalArchive": true,
    "IsAnalogArchive": true,
    "DepotOVoCode": "OVO001835"
  }
}
```

#### Parameters for plugin ‘mediahaven2.0’ {#dav-organisation-plugin-parameters}

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| NewsPaperClassification | NewspaperClassification | Add the newspaper classification. | No | False |

#### Parameters for plugin ‘dav’ {#dav-organisation-plugin-parameters}

| Property | Type | Description | Required | Default |
| --- | --- | --- | --- | --- |
| ApplicationScope | Enum(Erediensten,Gemeenten,Polders en wateringen,Provincies,Vlaamse overheid) | The application scope. | No |  |
| IsSelectionCommission | Boolean | Whether to configure the organisation as selection commission. | No | False |
| IsDigitalArchive | Boolean | Whether to configure the organisation as digital archive. | No | False |
| IsAnalogArchive | Boolean | Whether to configure the organisation as analog archive. | No | False |
| DepotOvoCode | String | Defines the depot to link to this analog archive. | Yes if IsAnalogArchive = true |  |
| IsDepot | boolean | Whether to configure the organisation as depot | No | False |
| DepotRequestOptions | Array of Enum(Scan,Borrow,Consult) | Defined the supported types for depot requests. | Yes if IsDepot = true |  |
| DefaultDepotRequestOption | Enum(Scan,Borrow,Consult) | Defines the default type for depot requests. | Yes if IsDepot = true |

## Organisation statistics {#organisation_stats}

### Description {#organisation_stats_description}

With this endpoint you can request the statistics of the organisation or installation. The storage statistics include
non-deleted and logically deleted records, permanently deleted records are never taken into account.
The statistics are only refreshed once a day and hence any changes are only reflected in the statistics the next day.

### Get statistics {#organisation_stats_get}

Retrieve [Statistics](#organisation_stats_object) using a `GET` request:
```
https://archief.viaa.be/mediahaven-rest-api/v2/organisations/{id}/stats
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| unit | The unit of storage size (B, KB, MB, GB, TB, PB) | Determined by size |

#### Response

- `200` A [Statistics](#organisation_stats_object)

#### Authorization functions

- Using this endpoint requires the `ADMIN_ORGANISATION` function.

### Organisation statistics object {#organisation_stats_object}

| Property | Type | Description |
| --- | --- | --- |
| Storage > Records > Value | number | The total filesize of all records |
| Storage > Records > Unit | Enum(B, KB, MB, GB, TB, PB) | The unit of the filesize |
| Storage > AipRecords > Value | number | The total filesize of all AIP records |
| Storage > AipRecords > Unit | Enum(B, KB, MB, GB, TB, PB) | The unit of the filesize |
| Objects > Groups > Total | number | The total number of groups |
| Objects > Records > Total | number | The total number of records |
| Objects > Records > Published | number | The total number of published records |
| Objects > Records > Archived | number | The total number of archived records |
| Objects > Records > Concept | number | The total number of records in concept |
| Objects > Records > Recycled | number | The total number of recycled records |
| Objects > AipRecords > Total | number | The total number of Aip records |
| Objects > AipRecords > Published | number | The total number of published aip records |
| Objects > AipRecords > Archived | number | The total number of archived aip records |
| Objects > AipRecords > Concept | number | The total number of aip records in concept |
| Objects > AipRecords > Recycled | number | The total number of recycled aip records |
| Objects > Users > Total | number | The total number of users |
| Objects > Users > Normal | number | The total number of normal users |
| Objects > Users > System | number | The total number of system users |
| Objects > Groups > Total | number | The total number of groups |
| Objects > Roles > Total | number | The total number of roles |
| Objects > Filters > Total | number | The total number of saved filters |
| Objects > Exports > Total | number | The total number of exports |
| Objects > Zones > Total | number | The total number of zones |

### Get global statistics {#organisation_stats_get_global}

Retrieve [Global statistics](#global_stats_object) using a `GET` request:
```
https://archief.viaa.be/mediahaven-rest-api/v2/stats
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| unit | The unit of storage size (B, KB, MB, GB, TB, PB) | Determined by size |

#### Response

- `200` A [Global statistics](#global_stats_object)

#### Authorization functions

- Using this endpoint requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Global statistics object {#global_stats_object}

| Property | Type | Description |
| --- | --- | --- |
| Storage > Records > Value | number | The total filesize of all records |
| Storage > Records > Unit | Enum(B, KB, MB, GB, TB, PB) | The unit of the filesize |
| Storage > AipRecords > Value | number | The total filesize of all AIP records |
| Storage > AipRecords > Unit | Enum(B, KB, MB, GB, TB, PB) | The unit of the filesize |
| Objects > Groups > Total | number | The total number of groups |
| Objects > Records > Total | number | The total number of records |
| Objects > Records > Published | number | The total number of published records |
| Objects > Records > Archived | number | The total number of archived records |
| Objects > Records > Concept | number | The total number of records in concept |
| Objects > Records > Recycled | number | The total number of recycled records |
| Objects > AipRecords > Total | number | The total number of Aip records |
| Objects > AipRecords > Published | number | The total number of published aip records |
| Objects > AipRecords > Archived | number | The total number of archived aip records |
| Objects > AipRecords > Concept | number | The total number of aip records in concept |
| Objects > AipRecords > Recycled | number | The total number of recycled aip records |
| Objects > Users > Total | number | The total number of users |
| Objects > Users > Normal | number | The total number of normal users |
| Objects > Users > System | number | The total number of system users |
| Objects > Groups > Total | number | The total number of groups |
| Objects > Roles > Total | number | The total number of roles |
| Objects > Filters > Total | number | The total number of saved filters |
| Objects > Exports > Total | number | The total number of exports |
| Objects > Zones > Total | number | The total number of zones |
| Objects > Organisations > Total | number | The total number of organisations |

## Zones {#zones}

Unpublished records (can) belong to a zone. Zones are used for sharing unpublished records between users belonging to
the same zone. All members of a zone can always read / edit all unpublished records within that zone.

Additional information can be found [here](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/3217850450/Zones).

### Required functions {#zone_functions}

The user requires the `ADMIN_ZONES` function to access the `/zones` endpoint. By default, only zones within the same
organisation as the user are accessible. Accessing zones from other organisations also requires
the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

To access the `/zones/:zoneId/users` endpoint, the `ADMIN_USERS` function is also required.

### Zone object structure {#zone_datamodel}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Id | String (UUID) | A unique zone id. | Yes |  |  |
| Name | String | A name to describe the zone | No | Empty | Yes |
| OrganisationId | Number | The id of the organisation the zone belongs to. | Yes once created. | Organisation of the user | No |
| GroupId | String (UUID) | The [group](#groups) linked with the zone which always acquires read, write and export rights on all unpublished records of the zone. | Yes |  | No |
| CreationDate | Date (ISO8601) | The date when the zone was created. | Yes |  |  |
| LastModifiedDate | Date (ISO8601) | The date when the zone was last modified. | Yes |  |

Example:
```
{
  "Id": "60aca242-97ff-47d6-97d5-0430a0882042",
  "Name": "My zone",
  "OrganisationId": 100,
  "GroupId": "b9f25e12-8e49-11eb-8dcd-0242ac130003",
  "LastModifiedDate": "2022-10-18T14:20:21.193000Z",
  "CreationDate": "2022-10-16T14:20:11.000000Z"
}
```

### Getting a specific zone {#specific_version}

Getting a specific zone is done by sending a GET-request to the following url.
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/:id
```

#### Response

- `200` Ok. [Zone](#zone_datamodel)
- `403` if the user does not have the required functions to call this method.
- `404` if the zone doesn’t exist.

### Get number of users linked to zone {#get_users_zone_count}

To get the total number of users linked to a zone, do a `HEAD` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/:id/users
```

The response will contain a header element with the name `Result-Count`.

#### Response

- `200` Ok.
- `401` User is not authorized
- `403` No access to the zone in question.
- `404` The zone does not exist.

### Listing all zones {#get_all_zones}

A list of all zones can be retrieved using a `GET` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Organisation to search in. Requires function ‘ADMIN_EDIT_ALL_ORGANISATIONS’ if searching in other organisations. | If user has the function `ADMIN_EDIT_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| userId | If set, only returns the zones the given user is a member of. | None |
| name | Name of the zone. Wildcards \* are allowed. |  |
| id | IngestSpaceId of zone |  |
| sort | Sort on one of the following fields (Name, Id, CreationDate, LastModifiedDate) | Name |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

#### Response

- `200` Ok. [Page](#page) of [Zones](#zone_datamodel)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

### Create zone {#create_zone}

To create a new zone you can send a `POST` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/
```

The endpoint supports json and xml with the following properties:

#### Zone object structure {#create_zone_datamodel}

| Property | Type | Description | Readonly | Default value | Required |
| --- | --- | --- | --- | --- | --- |
| Name | String | A name to describe the zone. Must be unique within the organisation. Only used when not converting an ingest space. | No | Empty | Only if IngestSpaceId is not provided |
| OrganisationId | Number | The id of the organisation the zone belongs to. Requires `ADMIN_EDIT_ALL_ORGANISATIONS` to change the default. Only used when not converting an ingest space. | No | Organisation of the user | No |
| IngestSpaceId | String | The id of an existing ingest space. This ingest space will be converted to a zone. | No | Empty | No |
| GroupId | String | The id of an existing group (only groups of type ‘NORMAL’ can be used). Only used when converting an ingest space. By default a new group will be created. | No | Empty | No |

Example request body:
```
{
  "Name": "Marketing",
  "OrganisationId": 100
}
```

```
{
  "IngestSpaceId": "fda68246-5678-4ae9-a7ab-c53cf530ec7e",
  "GroupId": "83b1e152-74ec-4b8b-8035-d44ca1998562"
}
```

#### Response

- `200` [created zone](#zone_datamodel)
- `400` one or more of the provided parameters are not valid
- `403` if the user does not have the required functions to call this method.
- `404` The provided resources (ie: organisation, ingest space, group) don’t exist
- `409` The ingest space was already converted to a zone

### Updating a zone {#update_zone}

Updating a zone can be done by performing a `PUT` request with a [Zone](#zone_datamodel) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/:id
```

Note that when changing the name, a re-index is required before the value of the `RightsManagement.Zone.Name` field of
records belonging to the zone is updated.

The endpoint supports json and xml.

#### Response

- `200` [updated zone](#zone_datamodel)
- `403` if the user does not have the required functions to call this method.
- `404` if the zone doesn’t exist.

### Deleting a zone {#deleting_zone}

Deleting a zone is done by simple sending a `DELETE` request to the following url.
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/:id
```

A zone can only be deleted if there are no non-deleted, unpublished records in the zone.

#### Response

- `204` if the zone was deleted successfully.
- `403` if the user does not have the required functions to call this method.
- `404` if the zone doesn’t exist.
- `409` if the zone can’t be deleted because it contains unpublished records.

### Listing user(s) from a zone {#zone_list_users}

To list all users linked to a zone, do a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/:zoneId/users
```

The standard [Page parameters](#page-filter) are available.

#### Authorization functions

- Using this endpoint requires the `ADMIN_USERS` function.

#### Response

- `200` A [Page](#page) of [Users](#user_object).
- `403` if the user does not have the required functions to call this method
- `404` if the zoneId is not found

### Adding user(s) to a zone {#zone_add_users}

To add one or more users to a zone, make a `POST` request to the following endpoint
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/:zoneId/users
```

with an array with the user ID/user IDs
```
[
  "<uuid of user>",
  ...
]
```

Please note that only 20 users can be added within a single request.

#### Authorization functions

- Using this endpoint requires the `ADMIN_USERS` function.

#### Response

- `204` if successful
- `400` if no users IDs are in the list
- `400` if the number of users is more than the number allowed within a single request.
- `403` if the user does not have the required functions to call this method
- `404` if the zoneId is not found
- `404` if one or more users are not found

### Removing user(s) from a zone {#zone_rem_users}

To remove one or more users from a zone, make a `DELETE` request to the following endpoint
```
https://archief.viaa.be/mediahaven-rest-api/v2/zones/:zoneId/users
```

with an array with the user ID/user IDs
```
[
  "<uuid of user>",
  ...
]
```

Please note that only 20 users can be removed within a single request.

#### Authorization functions

- Using this endpoint requires the `ADMIN_USERS` function.

#### Response

- `204` if successful
- `400` if no users IDs are in the list
- `400` if the number of users is more than the number allowed within a single request.
- `403` if the user does not have the required functions to call this method
- `404` if the zoneId is not found
- `404` if one or more users are not found

## Exports {#exports}

Exports jobs are created by using this resource and have an expiry time. Once an export job has completed, it’s
available for download from the provided URL. Once an export job expires, it will no longer appear in this resource and
it’s download URL will be invalid. A caching mechanism may be in effect which causes an export request to instantly
return a completed and downloadable export job.

### Export job status {#exports_status}

| Status | Description |
| --- | --- |
| Waiting | The job has been queued but not yet picked-up |
| InProgress | The job is being processed |
| Completed | The job has successfully finished; available for download |
| Failed | The job has unsuccessfully finished |
| Cancelled | An administrator cancelled the job |
| AlreadyExists | Advanced exports only: the exported file already exists at the destination |

### Creating export(s) {#exports_post}

Create export jobs using a `POST` request containing a [Export Request](#export-request).
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/exports
```

#### Response

- `201` List of [ExportJobs](#exports-job)
- `403` User lacks the export right to one or more records
- `400` The request sent is invalid
- `404` One or more records do not exist

### Getting all export jobs {#exports_get}

Retrieve a [Page](#page) of [ExportJobs](#exports-job) using a `GET` request
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/exports
```

The standard [Page parameters](#page-filter) are available. When the user does not have the function
`ADMIN_EXPORTS`, the results only contain the non-expired exports of user. If the user has the function
`ADMIN_EXPORTS`, the results contain the non-expired exports of all users. The results are sorted by the creation date
descending.

In addition to paging, the following query params are available:

| Query parameter | Description | Default |
| --- | --- | --- |
| tag | Filter on a specific tag (case-sensitive) |  |
| userId | Filter on this user ID (parameter is ignored unless the user has the function `ADMIN_EXPORTS`) |

> Note: you can use wildcards to filter on a partial tag.

#### Response

- `200` A [Page](#page) of [ExportJobs](#exports-job)

### Getting a specific export {#exports_get_single}

Retrieve a single [Export](#exports-job) using a `GET` request
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/exports/:exportJobId
```

#### Response

- `200` Single [ExportJob](#exports-job)
- `404` Export job was not found

### Delete export job {#exports_delete}

Delete an export job using a `DELETE` request:
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/exports/:exportJobId
```

#### Response

- `204` The export job was deleted.
- `404` Export job was not found

### Export Request object {#export-request}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Records.RecordId | String | `MediaObjectId`, `FragmentId` or `RecordId` of the record to export. |  |  |
| Records.Filename | String | The name of the record in the combined (ZIP) file. (Back)slashes are not allowed in the filename. | See `FilenameExpression` on export location | no |
| Records.Partial.Type | Enum (Bytes, Frames) | The type of the partial of the record. |  | no |
| Records.Partial.Start | Long | The `Start` from a half open interval [`Start`,`End`[ and must be between [0,`Duration`[ or [0,`Filesize`[ |  | no |
| Records.Partial.End | Long | The `End` from a half open interval [`Start`,`End`[ and must be between [0,`Duration` or [0,`Filesize`[ |  | no |
| Records.RepresentationId | String | A particular representation of the record to export. Only applicable for `Data` structure records. |  | no |
| Filename | String | The filename of the combined file to export. When exporting a single non-combined file, it also provides its filename if `Records[0].Filename` is not specified. | Empty String | no |
| ExportLocationId | String | The id of the export location the export should be stored at. | Empty String | no |
| Combine | Enum (Zip, ZipTree, Join, None) | See [Combine options](#combine_options) |  | no |
| Reason | String | The reason why this export was created . | Empty String | For some export locations |
| EventType | String | The eventype assigned to this export. | EXPORT | no |
| DestinationPath | String | The optional folder that the file(s) will be exported to on the destination, as defined in the export location. |  | no |
| ExportSource | ENUM (Original, Access, OriginalAndAccess) | What source to use. If `null` fallback to the obsolete property `UseOriginal`. |  |  |
| UseOriginal | Boolean | Obsolete, use `ExportSource` instead, whether to export the original (default) or the browse. | true | no |
| Options.Metadata.Type | ENUM (Sidecar, Burn) | If set, defines how record metadata is exported. The option ‘Sidecar’ means the metadata is exported as a separate [sidecar](#sidecar_format) file. | Sidecar |  |
| Options.Metadata.Format | ENUM (Mediahaven, DublinCore, Mets, MetsMhs, MetsMhsTree, Mhs, MetsMhsHead, MetsMhsTreeHead, MhsHead) | Only allowed when `Options.Metadata.Type` = `Sidecar`, the [sidecar format](#sidecar_format). | MediaHaven |  |
| Options.Metadata.OnlyMetadata | Boolean | Only allowed when `Options.Metadata.Type` = `Sidecar`, if set to true, only the sidecar metadata will be exported. | false |  |
| Options.Metadata.MetadataTranslationId | UuidV4 | Only allowed when `Options.Metadata.Type` = `Burn`, refers to a valid [metadata translation](#metadata_translation). |  |  |
| Options.Video.Height | Number | The height in pixels an exported video will have. If not defined, the original height will be used. | Value defined on export location. | no |
| Options.Video.Width | Number | The width in pixels an exported video will have. If not defined, the original width will be used. | Value defined on export location. | no |
| Options.Video.Bitrate | Number | The bitrate in bits per second an exported video will have. If not defined, the original bitrate will be used. | Value defined on export location. | no |
| Options.Video.Container | ENUM (MP4,FLV,AVI,WMV,PRORES) | The export container format. If not defined, the original format will be used. | Value defined on export location. | no |
| Options.Video.Channels | Number | The number of audio channels. | Value defined on export location. | no |
| Options.Audio.SampleRate | Number | The sample rate in hertz an exported audio file will have. If not defined, the original sample rate will be used. | Value defined on export location. | no |
| Options.Audio.Bitrate | Number | The bitrate in bits per second an exported audio file will have. If not defined, the original bitrate will be used. | Value defined on export location. | no |
| Options.Audio.Container | ENUM (MP3,WAV,AIFF,AAC,OGG,WMA,FLAC) | The file format an exported audio-only file will have. Not applicable if file contains video as well. If not defined, the original format will be used. | Value defined on export location. | no |
| Options.Image.Height | Number | The height in pixels an exported image will have. If not defined, the original height will be used. | Value defined on export location. | no |
| Options.Image.Width | Number | The width in pixels an exported image will have. If not defined, the original width will be used. | Value defined on export location. | no |
| Options.Image.Container | ENUM (JPG,PNG,TIFF,PDF) | The export container format, defaults to JPG when transforming and not explicitly set. | Value defined on export location. | no |
| Options.Image.ColorSpace | ENUM (sRGB,CMYK,RGB,LAB,AdobeRGB) | The color space of the export, defaults to sRGB when transforming and not explicitly set. | Value defined on export location. | no |
| Options.Image.Cropping.Top | Number | The offset from the top to crop the image. Value should be equal or larger than 0. | Value defined on export location. | no |
| Options.Image.Cropping.Bottom | Number | The offset from the bottom to crop the image. Value should be equal or larger than 0. | Value defined on export location. | no |
| Options.Image.Cropping.Left | Number | The offset from the left to crop the image. Value should be equal or larger than 0. | Value defined on export location. | no |
| Options.Image.Cropping.Right | Number | The offset from the right to crop the image. Value should be equal or larger than 0. | Value defined on export location. | no |
| Options.Image.Rotate | Number | The rotation of the image, in degrees (minimum 0, max 360) | Value defined on export location. | no |
| Options.Image.Flip | ENUM(HORIZONTAL,VERTICAL) | Flip the image horizontal / vertical | Value defined on export location. | no |
| Options.Document.Height | Number | The height in pixels an exported image will have. If not defined, the original height will be used. | Value defined on export location. | no |
| Options.Document.Width | Number | The width in pixels an exported image will have. If not defined, the original width will be used. | Value defined on export location. | no |
| Options.Document.Container | ENUM (JPG,PNG,TIFF,PDF,ODT) | The export container format, defaults to JPG when transforming and not explicitly set. | Value defined on export location. | no |
| Options.Document.ColorSpace | ENUM (sRGB,CMYK,RGB,LAB,AdobeRGB) | The color space of the export, defaults to sRGB when transforming and not explicitly set. | Value defined on export location. | no |
| Tag | String | Optional property that can be used when retrieving exportjobs. | Empty String | no |

> Note: When exporting a `Data` structure record, you can select which representation under the data object you actually want to export:
> - Export a particular representation, using `Records.RepresentationId`
> - Export the original representation, using `UseOriginal = true` (only if RepresentationId is empty)
> - Export the access representation, using `UseOriginal = false` (only if RepresentationId is empty)
```
{
  "Records": [
    {
      "RecordId": "c6b929e29e1b4300935ac049a5db74550566a5a28f64403e957312bb1e35eab1",
      "Filename": "test",
      "Partial": {
        "Type": "Frames",
        "Start": 84616546513513,
        "End": 654151897465156987
      }
    }
  ],
  "Filename": "big test",
  "ExportLocationId": "5",
  "Combine": "ZIP",
  "Reason": "move all tests to dedicated test location",
  "EventType": "EXPORT",
  "DestinationPath": "",
  "UseOriginal": false,
  "Options": {
    "Metadata": {
      "Type": "Sidecar",
      "Format": "Mhs",
      "OnlyMetadata": true
    },
    "Video": {
      "Height": 300,
      "Width": 600,
      "Bitrate": 8,
      "Container": "FLV",
      "Channels": 2
    },
    "Audio": {
      "SampleRate": 25,
      "Bitrate": "8",
      "Container": "FLAC"
    }
  },
  "Tag": "CONSULTATION"
}
```

#### Combine options {#combine_options}

- ZipTree: Include all childOf relations recursively
- Zip: return zip with all exported records
- Join: Will join the video or audio records in one file

#### EventType limitations

- Cannot start with `EXPORT`
- Can only contain alphanumeric characters and -, _ or .
- We will always add the prefix `EXPORT.` to the provided event type

#### Partial limitations:

- `Start` or `End` is required; the other will be prefilled with start or end of the file
- Type `Frames`: `Start` and `End` form a half open interval [`Start`,`End`[ and must be between [0,`Duration`[
- Type `Frames` is only supported for video or audio
- Type `Bytes`: `Start` and `End` form a closed inclusive interval [`Start`,`End`] and must be between [0,`FileSize`[
- Type `Bytes` is not allowed for 0 bytes records

### Export Job object {#exports-job}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| ExportJobId | String | Unique identifier. |  | no |
| Name | String | Provided filename during the export request or the file name resulting from the expression defined at the export location. |  | no |
| RecordId | String | `MediaObjectId`, `FragmentId` or `RecordId` of the exported record. | null | no |
| Status | String | See table above for the possible values. | waiting | no |
| Progress | Float | Between 0.0 and 1.0. | 0 | no |
| DownloadUrl | String | The url where the exported record can be downloaded, empty string before status is completed. | empty string | no |
| RemoteUrl | String | The remote uri of the exported record (only visible for users with the function `ADMIN_EXPORTS`) | 0 | no |
| CreationDate | Date (ISO8601) | The date when the job was created. | null | no |
| StartDate | Date (ISO8601) | The date when the status became `InProgress`. | null | no |
| FinishDate | Date (ISO8601) | The date when the status became no longer InProgress, null when status Waiting or InProgress. | null | no |
| ExpiryDate | Date (ISO8601) | The date when the exportjob wil expire. | null | no |
| Tag | String | Optional property that can be used when retrieving exportjobs. | empty string | no |

> For property `Name`, the following rules apply:
> - When the filename expression defined at the export location yields a runtime error, the original filename of the record is used.
> - The maximum length for this value is 255 characters. When this limit is exceeded, the name is truncated.
```
{
  "ExportJobId": "20210326_120035_6ef509f8c90741f1a64ba77c568faed7e57f0b0f2d8f48329b95b3d498767455_zeticon@dev_b93e1559-bc8e-4a87-8149-4e71509c69e0",
  "Name": "#skateboarding.mp4",
  "RecordId": "6ef509f8c90741f1a64ba77c568faed7e57f0b0f2d8f48329b95b3d49876745564c00a981209448587898b9f42707497",
  "Status": "Waiting",
  "Progress": 0.0,
  "DownloadUrl": "",
  "RemoteUrl": "",
  "CreationDate": "2021-03-26T11:00:35.485000Z",
  "StartDate": "2021-03-26T11:00:35.579000Z",
  "FinishDate": "2021-03-26T11:00:35.579000Z",
  "ExpiryDate": "2021-03-26T11:00:35.579000Z",
  "Tag": "CONSULTATION"
}
```

## Export locations {#export_locations}

### Listing all export locations {#get_all_export_locations}

A list of all export locations can be retrieved using a `GET` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| sort | Sort on one of the following fields (CreationDate, LastModifiedDate) | CreationDate |
| direction | The direction can be `asc`, `up`, `desc` or `down` | desc |
| organisationId | Organisation to search in | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |

> Note: A user without the ADMIN_EXPORTS or ADMIN_VIEW_ALL_ORGANISATIONS function can only see export locations to which
> the user has access (i.e. export locations explicitly linked to the user and export locations allowed for all users
> and
> part of the user’s organisation).

#### Response

- `200` A [Page](#page) of [Export locations](#export_locations_object)
- `400` The request is not valid
- `403` The user does not have the required functions to call this method

#### Authorization functions

- Requesting all export locations for an organisation, regardless of the user accessibility, requires
  the `ADMIN_EXPORTS` or `ADMIN_VIEW_ALL_ORGANISATIONS` function.
- Requesting export locations of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Getting an export location {#fetching_export_location}

A single export location can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations/:id
```

#### Response

- `200` Ok. Body: [Export location](#export_locations_object)
- `403` User has no access to the export location
- `404` The export location does not exist

#### Authorization functions

- Requesting an export location of the user’s organisation which is not accessible for the user itself, requires
  the `ADMIN_EXPORTS` or `ADMIN_VIEW_ALL_ORGANISATIONS` function.
- Requesting an export location of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Creating an export location {#create_export_location}

An export location can be created by performing a `POST` request with [Export location](#export_locations_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| saveCredentials | If true, the credentials from `Server.Username` and `Server.Password` will overwrite the credentials. | false |

#### Response

- `200` Ok. Body: [Export location](#export_locations_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the export location in question.

#### Authorization functions

- Using this endpoint requires the `ADMIN_EXPORTS` function.
- Creating an export location for a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Update an export location {#update_export_location}

Updating an export location can be done by performing a PUT-request with [Export location](#export_locations_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations/:id
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| saveCredentials | If true, the credentials from `Server.Username` and `Server.Password` will overwrite the credentials. | false |

#### Response

- `200` Ok. Body: Updated [export location](#export_locations_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the export location in question.
- `404` The export location could not be found

#### Authorization functions

- Using this endpoint requires the `ADMIN_EXPORTS` function.
- Updating an export location for a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Delete an export location {#delete_export_location}

An export location can be deleted by performing a `DELETE` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations/:id
```

#### Response

- `204` The export location was deleted.
- `403` No access to the export location in question or the export location is not deletable.
- `404` The export location does not exist.

#### Authorization functions

- A user with the `ADMIN_EXPORTS` function can delete an export location.
- Deleting an export location of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Retrieve all users linked to an export location {#get_users_export_location}

In order to get a complete list of all users linked to an export location, do a `GET` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations/:id/users
```

#### Response

- `200` Ok. [Page](#page) of [Users](#user_object)
- `403` No access to the export location in question.
- `404` The export location does not exist.

#### Authorization functions

- Using this endpoint requires the `ADMIN_USERS` and `ADMIN_EXPORTS` function.
- Requesting the users of an export location of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS`
  function.

### Get number of users linked to an export location {#get_users_export_location_count}

To get the total number of users linked to an export location, do a `HEAD` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations/:id/users
```

The response will contain a header element with the name `Result-Count`.

#### Response

- `200` Ok.
- `401` User is not authorized
- `403` No access to the export location in question.
- `404` The export location does not exist.

#### Authorization functions

- Using this endpoint requires the `ADMIN_USERS` or `ADMIN_EXPORTS` function.
- Requesting the number of users of an export location of a different organisation requires
  the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Update users of an export location {#update_users_export_location}

Export location users can be updated by performing a `PUT` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations/:id/users
```

with an array of user ids:
```
[
  "<uuid of user>",
  ...
]
```

#### Response

- `204` Users were updated.
- `400` Bad request: [error result](#error)
    - User can not be linked to an export location of another organisation.
    - Export location allowed for all users or all organisations can not be linked to users.
- `403` No access to the export location in question.
- `404` The export does not exist or one or more of the user ids do not exist.

#### Authorization functions

- Updating users requires the function `ADMIN_USERS` and `ADMIN_EXPORTS` function.
- Updating the users of an export location of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS`
  function.

### Getting the default export location {#fetching_default_export_location}

The default export location can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/export-locations/default
```

#### Response

- `200` Ok. Body: [Export location](#export_locations_object)

### Export locations object structure {#export_locations_object}

| Property | Type | Description | Default value | Required | ReadOnly |
| --- | --- | --- | --- | --- | --- |
| Id | String | The exportLocationId | -1 |  |  |
| Name | String | User-presentable name of the location |  | yes |  |
| UniqueFolder | Boolean | Whether each export to this location creates a unique subfolder for the export | true |  |  |
| HttpAccessible | Boolean | Whether the result of the export can be downloaded |  |  | true |
| HttpUrl | String | The (internal) url on which the export will be accessible (only visible for users with the function ADMIN_EXPORTS) |  | yes, if Default = true |  |
| ExportReasonRequired | Boolean | Whether an export reason is required to initiate an export | false |  |  |
| ExportReasons | String[] | A list of export reasons to pick from |  |  |  |
| CustomExportReasonAllowed | Boolean | Whether a custom (free-text) reason is allowed in addition to the supplied list | true |  | true |
| ZipExportAllowed | Boolean | `Deprecated, use Context.Combine instead` Whether zip exports are supported for this export location | true |  | true |
| BrowseExportAllowed | Boolean | `Deprecated, use Context.Source instead` Whether browse exports are supported for this export location | true |  | true |
| Options.Metadata.Type | ENUM (Sidecar, Burn) | If set, defines how record metadata is exported. Currently the only option is ‘Sidecar’, which means the metadata is exported as a separate [sidecar](#sidecar_format) file. | Sidecar |  |  |
| Options.Metadata.Format | ENUM (Mediahaven, DublinCore, Mets, MetsMhs, MetsMhsTree, Mhs, MetsMhsHead, MetsMhsTreeHead, MhsHead) | Only allowed when `Options.Metadata.Type` = `Sidecar`, the [sidecar format](#sidecar_format). | MediaHaven (if `Options.Metadata.Type` = `Sidecar`) |  |  |
| Options.Metadata.OnlyMetadata | Boolean | Only allowed when `Options.Metadata.Type` = `Sidecar`, if set to true, only the sidecar metadata will be exported. | false |  |  |
| Options.Metadata.MetadataTranslationId | UuidV4 | Only allowed when `Options.Metadata.Type` = `Burn`, refers to a valid [metadata translation](#metadata_translation). |  | yes, if `Options.Metadata.Type` = `Burn` |  |
| Options.Video.Height | Number | The height in pixels an exported video will have. If not defined, the original height will be used. |  |  |  |
| Options.Video.Width | Number | The width in pixels an exported video will have. If not defined, the original width will be used. |  |  |  |
| Options.Video.Bitrate | Number | The bitrate in bits per second an exported video will have. If not defined, the original bitrate will be used. |  |  |  |
| Options.Video.Container | ENUM (MP4,FLV,AVI,WMV,MOV,PRORES) | The export container format. If not defined, the original format will be used. |  |  |  |
| Options.Video.Channels | Number | The number of audio channels. |  |  |  |
| Options.Video.Watermark.Source | String | The source of the watermark applied by the transformation. |  | yes (if Watermark is defined) |  |
| Options.Video.Watermark.Scale | Number | The scale of the watermark. | 100 |  |  |
| Options.Video.Watermark.Opacity | Number | The opacity of the watermark. | 100 |  |  |
| Options.Video.Watermark.Position | Enum (CENTER, TILED, NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST) | The position of the watermark. | CENTER |  |  |
| Options.Video.Subtitle | String | The subtitle. |  |  |  |
| Options.Audio.SampleRate | Number | The sample rate in hertz an exported audio file will have. If not defined, the original sample rate will be used. |  |  |  |
| Options.Audio.Bitrate | Number | The bitrate in bits per second an exported audio file will have. If not defined, the original bitrate will be used. |  |  |  |
| Options.Audio.Container | ENUM (MP3,WAV,AIFF,AAC,OGG,WMA,FLAC) | The file format an exported audio-only file will have. Not applicable if file contains video as well. If not defined, the original format will be used. |  |  |  |
| Options.Image.Height | Number | The height in pixels an exported image will have. If not defined, the original height will be used. |  |  |  |
| Options.Image.Width | Number | The width in pixels an exported image will have. If not defined, the original width will be used. |  |  |  |
| Options.Image.Container | ENUM (JPG,PNG,TIFF,PDF) | The export container format, defaults to JPG when transforming and not explicitly set. |  |  |  |
| Options.Image.ColorSpace | ENUM (sRGB,CMYK,RGB,LAB,AdobeRGB) | The color space of the export, defaults to sRGB when transforming and not explicitly set. |  |  |  |
| Options.Image.Cropping.Top | Number | The offset from the top to crop the image. Value should be equal or larger than 0. |  |  |  |
| Options.Image.Cropping.Bottom | Number | The offset from the bottom to crop the image. Value should be equal or larger than 0. |  |  |  |
| Options.Image.Cropping.Left | Number | The offset from the left to crop the image. Value should be equal or larger than 0. |  |  |  |
| Options.Image.Cropping.Right | Number | The offset from the right to crop the image. Value should be equal or larger than 0. |  |  |  |
| Options.Image.Rotate | Double | The rotation of the image, in degrees (minimum 0, max 360) |  |  |  |
| Options.Image.Flip | ENUM (HORIZONTAL,VERTICAL) | Flip the image horizontal / vertical |  |  |  |
| Options.Image.Watermark.Source | String | The source of the watermark applied by the transformation. |  | yes (if Watermark is defined) |  |
| Options.Image.Watermark.Scale | Number | The scale of the watermark. | 100 |  |  |
| Options.Image.Watermark.Opacity | Number | The opacity of the watermark. | 100 |  |  |
| Options.Image.Watermark.Position | Enum (CENTER, TILED, NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST) | The position of the watermark. | CENTER |  |  |
| Options.Document.Height | Number | The height in pixels an exported image will have. If not defined, the original height will be used. |  |  |  |
| Options.Document.Width | Number | The width in pixels an exported image will have. If not defined, the original width will be used. |  |  |  |
| Options.Document.Container | ENUM (JPG,PNG,TIFF,PDF,ODT) | The export container format, defaults to JPG when transforming and not explicitly set. |  |  |  |
| Options.Document.ColorSpace | ENUM (sRGB,CMYK,RGB,LAB,AdobeRGB) | The color space of the export, defaults to sRGB when transforming and not explicitly set. |  |  |  |
| Options.Document.Watermark.Source | String | The source of the watermark applied by the transformation. |  | yes (if Watermark is defined) |  |
| Options.Document.Watermark.Scale | Number | The scale of the watermark. | 100 |  |  |
| Options.Document.Watermark.Opacity | Number | The opacity of the watermark. | 100 |  |  |
| Options.Document.Watermark.Position | Enum (CENTER, TILED, NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST) | The position of the watermark. | CENTER |  |  |
| Context.Combine | String[] | Lists which [combine options](#combine_options) are supported. |  |  | yes |
| Context.Source | String[] | Lists which sources are supported. Possible values are:  *Original*  Browse |  |  | yes |
| Context.MetadataType | String[] | Lists which values are supported for `Options.Metadata.type` when using combine options `None` or `Join`. |  |  | yes |
| Context.MetadataTypeForZip | String[] | Lists which values are supported for `Options.Metadata.type`when using combine options `Zip` or `ZipTree`. |  |  | yes |
| Context.MultipleFiles | Boolean | Whether the export location supports requests that output multiple files, i.e. combine option `None` with multiple records and/or sidecar metadata. |  |  | yes |
| Context.Transformation | Boolean | Whether the various transformation options under `Options.Audio` and `Options.Video` can be used. |  |  | yes |
| Context.VideoContainers | ENUM[] (MP4,FLV,AVI,WMV,MOV,PRORES) | Available video containers to choose from, if `Options.Video.Container` is provided then the context is restricted to that container. |  |  | yes |
| Context.AudioContainers | ENUM[] (MP3,WAV,AIFF,AAC,OGG,WMA,FLAC) | Available audio containers to choose from, if `Options.Audio.Container` is provided then the context is restricted to that container. |  |  | yes |
| Context.PredefinedOptions | String[] | List of options that are disabled for export requests because they are predefined. |  |  | yes |
| Context.IsEditable | Boolean | Whether the export location is editable. |  |  | yes |
| Context.AreOptionsEditable | Boolean | Whether the options of the export location are editable. |  |  | yes |
| Context.IsDeletable | Boolean | Whether the export location is deletable. |  |  | yes |
| CreationDate | Date (ISO8601) | The date when the export location was created. |  |  | yes |
| LastModifiedDate | Date (ISO8601) | The date when the export location was last modified. |  |  | yes |
| OrganisationId | Number | The id of the organisation the export location belongs to. |  | yes |  |
| AllowedForAllOrganisations | Boolean | Whether the export location is allowed for all organisations. | false |  |  |
| AllowedForAllUsers | Boolean | Whether the export location is allowed for all users. | false |  |  |
| Default | Boolean | Whether the export location is the default export location. | false |  |  |
| Priority | Number | The priority (number between 1 and 4). | 1 |  |  |
| Protocol | ENUM (Ftp, FtpActive, Ftps, FtpsActive, Castor, S3, Azure, Glacier, Jwplayer, Youtube) | The server protocol. |  | yes (if StoragePoolId not defined) |  |
| StoragePoolId | Number | The id of the storage pool. |  | yes (if Server not defined) |  |
| Server.Address | String | The server address. |  | yes (if StoragePoolId not defined) |  |
| Server.Port | Number | The server port. | 21 |  |  |
| Server.Username | String | The server username. Write-only, will be overwritten when the parameter `saveCredentials` is true, otherwise returned as `<hidden value>`. |  |  |  |
| Server.Password | String | The server password. Write-only, will be overwritten when the parameter `saveCredentials` is true, otherwise returned as `<hidden value>`. |  | On create when username is defined |  |
| Server.Path | String | The server path. | \/ |  |  |
| TempLocation.Path | String | The temporary location path. |  |  |  |
| TempLocation.Filename | String | The temporary filename + extension. |  |  |  |
| FilenameExpression | SpEL expression | Expression that will provide the filename of the export. | #{R(‘Descriptive.OriginalFilename’)} |  |

> Note: The property `FilenameExpression` can be used to support custom filenames for exports. An expression of the form `#{...}` can be used for this, which allows a strict subset of the Spring Expression Language (SpEL). See [Export](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/3502768171/Export) for a more detailed explanation.
```
{
  "Id": "10",
  "Name": "Test_doc",
  "HttpAccessible": false,
  "ExportReasonRequired": false,
  "ExportReasons": [
    "test",
    "lost file"
  ],
  "CustomExportReasonAllowed": false,
  "ZipExportAllowed": true,
  "BrowseExportAllowed": true,
  "Options": {
    "Metadata": {
      "Type": "Sidecar",
      "Format": "Mets",
      "OnlyMetadata": false,
      "IsEditable": true,
      "AreOptionsEditable": true,
      "IsDeletable": true
    },
    "Video": {
      "Height": 300,
      "Width": 600,
      "Bitrate": 8,
      "Container": "FLV",
      "Subtitle": "subtitle",
      "Watermark" : {
        "Source": "",
        "Scale": 100,
        "Opacity": 100,
        "Position": "NORTH"
      }
    },
    "Audio": {
      "SampleRate": 25,
      "Bitrate": "8",
      "Container": "FLAC"
    }
  },
  "Context": {
    "Combine": [
      "Join",
      "Zip",
      "ZipTree",
      "None"
    ],
    "Source": [
      "Original",
      "Browse"
    ],
    "MetadataType": [
      "Sidecar"
    ],
    "MetadataTypeForZip": [],
    "Transformation": true,
    "MultipleFiles": true,
    "PredefinedOptions": [
      "Video",
      "Audio",
      "Metadata"
    ]
  },
  "LastModifiedDate": "2022-10-18T14:20:21.193000Z",
  "CreationDate": "2022-10-16T14:20:11.000000Z",
  "OrganisationId" : 100,
  "AllowedForAllOrganisations": false,
  "AllowedForAllUsers": false,
  "Protocol": "Ftp",
  "StoragePoolId": 3,
  "Default": false,
  "Priority": 2,
  "TempLocation" : {
    "Path": "/temp/",
    "Filename": "filename.txt"
  },
  "FilenameExpression" : "#{R('Descriptive.OriginalFilename')}"
}
```

## Batches {#batches}

Batches operate on a large data set conveyed via a filter. The data set is then linked to a one of various tasks. After
creation, the status of the batch can be monitored.

### Getting all batches {#batches_get_all}

Retrieve a [Page](#page) of [Batches](#batch_object) using a `GET` request
```
https://archief.viaa.be/mediahaven-rest-api/v2/batches
```

The standard [Page parameters](#page-filter) are available.

In addition to paging, the following query params are available:

| Query parameter | Description | Default |
| --- | --- | --- |
| tag | Filter on a specific tag (case-sensitive) |  |
| label | The label of the batch |  |
| sort | Sort on one of the following fields (CreationDate, StartDate, FinishDate, Label) | CreationDate |
| direction | The direction can be `asc`, `up`, `desc` or `down` | desc |
| userId | Id of user to filter on | current |
| index | Filter on index | current |
| taskType | Filter on the type of task that will be executed on the specified files. It’s possible to filter on multiple task types. |  |
| status | Filter on the current status of the batch. It is possible to filter on multiple statuses. Possible values: Waiting, Processing, Completed, CompletedWithErrors, Cancelled, PostBatchFailed, TooManyFailed |

> Note: you can use wildcards to filter on a tag and label.

#### Response

- `200` A [Page](#page) of [Batches](#batch_object)
- `400` The request is not valid

#### Authorization functions

- A user with the `ADMIN_BATCHES` function can see all batches linked with the index of the organisation of the current
  user
- A user with the `ADMIN_BATCHES` and `ADMIN_VIEW_ALL_ORGANISATIONS` can see all batches
- The index is forced to current when user does not have the function `ADMIN_VIEW_ALL_ORGANISATIONS`
- The userId is forced to current when user does not have function `ADMIN_BATCHES`

### Getting a specific batch {#batches_get_single}

Retrieve a single [Batch](#batch_object) using a `GET` request
```
https://archief.viaa.be/mediahaven-rest-api/v2/batches/:id
```

#### Response

- `200` Single [Batch](#batch_object)
- `404` Batch was not found

### Creating a batch {#batches_post}

Creating a batch can be done by performing a `POST` request containing a [Create Batch](#create_batch_object):
```
https://archief.viaa.be/mediahaven-rest-api/v2/batches
```

#### Response

- `200` The created [Batch](#batch_object)
- `400` The request is not valid
- `403` User is not authorized

### Partial updating a batch {#batches_post}

A batch can be partially updated by performing a `PATCH`-request containing a [Partial Update Batch](#partial_update_batch_object):
```
https://archief.viaa.be/mediahaven-rest-api/v2/batches
```

Notes:
- Only values provided in the patch will be overwritten.
- Only batches which are not finished yet can be updated (`Active` should be greater than 0)

#### Response

- `200` Ok. Body: Partial updated [Batch](#batch_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the batch
- `404` The batch could not be found
- `409` The batch cannot be updated in its current status

#### Authorization functions

- Partial updating a batch requires the function `ADMIN_BACKEND_SERVICES`.
- Partial updating your personal batches requires no additional function.
- Partial updating batches of your organisation requires the additional function `ADMIN_BATCHES`.
- Partial updating batches of other organisations requires the additional functions `ADMIN_BATCHES` and `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Get number of active batches {#get_active_batches_count}

To get the total number of all active batches for an organisation, do a `HEAD` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/batches/active
```

| Query parameter | Type | Description | Default Value |
| --- | --- | --- | --- |
| organisationId | Number | Organisation to filter on. | Organisation of user |

The response will contain a header element with the name `Result-Count`.

> Note: the requesting user does not necessarily have access to all batches included in the total number.

#### Response

- `200` Ok.

#### Authorization functions

- Getting the number of active batches for other organisations requires either the `ADMIN_VIEW_ALL_ORGANISATIONS`
  function or the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### List the failed records for a batch {#batches_failures}

The failed records for a batch can be fetched by performing a GET request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/batches/:id/failures
```

The standard [Page parameters](#page-filter) are available.

> Note: If too many records fail, the batch is aborted and assigned the status `TooManyFailed`. As a result, only a limited number of failed records are stored.

#### Response

- `200` A [Page](#page) of [Batch record failures](#batch_record_failure_object)
- `400` One or more of the provided property values were not valid.
- `401` User is not authorized.
- `404` Batch was not found.

### Cancelling a batch {#batches_cancel}

A batch can be cancelled by performing a DELETE-request to the following endpoint:
```
https:/archief.viaa.be/mediahaven-rest-api/v2/batches/:id
```

> Note: The cancellation sets the batch status to `Cancelling` and let the existing jobs finish. New jobs are no longer created. Once the jobs are completed, the batch status changes to `Cancelled`

#### Response

- `202` The batch will be cancelled
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the batch
- `404` The batch could not be found
- `409` The batch cannot be cancelled in its current status

#### Authorization functions

- Cancelling a batch requires the function `ADMIN_BACKEND_SERVICES`.
- Cancelling your personal batches requires no additional function.
- Cancelling batches of your organisation requires the additional function `ADMIN_BATCHES`.
- Cancelling batches of other organisations requires the additional functions `ADMIN_BATCHES` and `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Batch object {#batch_object}

| Property | Type | Description |
| --- | --- | --- |
| TaskType | String | The type of task that will be executed on the specified files. |
| Task | Task | The task object of type TaskType. |
| Id | String | The id of this batch. |
| Status | Enum | Status of the batch: `Waiting`, `Processing`, `Completed`, `CompletedWithErrors`, `PostBatchFailed`, `TooManyFailed`, `Cancelling`, `Cancelled` |
| UserId | String (UUID) | The id of the user who initiated the batch. |
| SearchRequest.Query | String | The Solr query with which the specified records can be selected for this batch. |
| SearchRequest.SortField | String | The field on which the records will be sorted. |
| SearchRequest.SortDirection | String | Implicates the way the records are sorted( Ascending/Descending) based on the SortField. |
| Label | String | The label to identify the batch. |
| Slices | Number | The number of parallel jobs, ranging from 1 to 128. For regular batches the limit is 1. |
| Active | Number | Shows how many active jobs there are. |
| Completed | Number | The number of jobs that are successfully completed. |
| Skipped | Number | The number of jobs that are skipped. |
| Failed | Number | The number of jobs that failed. |
| Total | Number | The number of jobs that were appended in this batch. |
| CreationDate | Date (ISO8601) | The date when the batch was created. |
| StartDate | Date (ISO8601) | The date the batch started. |
| FinishDate | Date (ISO8601) | The date the batch actually ended. |
| Estimate | Date (ISO8601) | The estimated end date of the batch. |
| Propagate | boolean | If the batch changes for a record a metadata [field](#field_definitions_json_flat) with inheritance propagation, propagate these changes. |
| Indices | String[] | The list of indices the batch will use to search for records. |
| Errors | String[] | `Deprecated property, might be removed in the future.` List of errors that occurred during execution of this batch. Only up to a certain number of errors are stored |
| Tag | String | The tag for the batch. |
| Priority | Enum (High, Normal, Low, Background) | The priority of the batch. |
| Zone | String | The zone of the worker daemon for this batch. |

> Note: The `Errors` property is deprecated. Instead, the [Batches failures endpoint](#batches_failures) can be used to inspect the failed records for a batch.

Example:
```
{
  "Id": "a317ba29-4b6f-40c1-96aa-f35af7ab64ba",
  "UserId": "866050f2-1480-4403-8fec-c10efd38e164",
  "SearchRequest": {
    "Query": "+Descriptive.Title:test",
    "SortField": "Administrative.ArchiveDate",
    "SortDirection": "Asc"
  },
  "Active": 0,
  "Completed": 0,
  "Skipped": 0,
  "Failed": 0,
  "Total": 0,
  "Slices": 0,
  "CreationDate": "2021-03-26T09:38:34.188000Z",
  "StartDate": "2021-03-26T09:38:34.188000Z",
  "FinishDate": null,
  "Estimate": null,
  "Label": "BatchMergeTask",
  "Propagate": false,
  "TaskType": "BatchMergeTask",
  "Indices": [
    "beeldbank-mgmt"
  ],
  "Task": {
    ...
  },
  "Tag": "Archive",
  "Priority": "LOW"
}
```

The properties “TaskType” and “Task” are one of the following [possibilities](#task_object).

### Batch create object {#create_batch_object}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| TaskType | String | The type of task that will be executed on the specified files. |  | yes |
| Task | Task | The task object of type TaskType. |  | yes |
| SearchRequest.Query | String | The Solr query with which the specified records can be selected for this batch. |  | yes |
| SearchRequest.SortField | String | The field on which the records will be sorted. | empty list | no |
| SearchRequest.SortDirection | String | Implicates the way the records are sorted( Ascending/Descending) based on the SortField. |  | no |
| Label | String | The label to identify the batch. |  | no |
| Slices | Number | The number of parallel jobs, ranging from 1 to 128. | 1 | no |
| Propagate | boolean | If the batch changes for a record a metadata [field](#field_definitions_json_flat) with inheritance propagation, propagate these changes. | false | no |
| Indices | String[] | The list of indices the batch will use to search for records. | all indices the user has access to | no |
| Tag | String | The tag for the batch. |  | no |
| Priority | Enum (High, Normal, Low, Background) | The priority of the batch. | Normal | no |
| Zone | String | The zone of the worker daemon for this batch. |  | no |

### Batch partial update object {#partial_update_batch_object}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Label | String | The label to identify the batch. |  | no |
| Tag | String | The tag for the batch. |  | no |
| Priority | Enum (High, Normal, Low, Background) | The priority of the batch. | Normal | no |
| Zone | String | The zone of the worker daemon for this batch. |  | no |

### Batch record failure object {#batch_record_failure_object}

| Property | Type | Description |
| --- | --- | --- |
| RecordId | String (UUID) | The record id to which the failure apply. |
| ErrorMessage | String | Error message of the failure. |

### Tasks {#task_object}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| TaskType | String | The name of the task you want to execute |  | yes |
| Task | String | A json object with the attributes needed for a specific task |  | yes |

#### Merge {#task_object_merge}

Batch action used to merge all records referred by the search request. The task property “Sidecar” is
a [Record object](#record-object).

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Sidecar | [Sidecar](#sidecar_format) | The record to be merged |  | yes |
| Reason | String | The reason why the task is being executed |  | yes |
| SubType | String | The subevent type for the update event |  | no |
```
{
  "TaskType": "BatchMergeTask",
  "Task": {
    "Sidecar": "<record>",
    "Reason": "changed the footer",
    "SubType": ""
  }
}
```

#### Merges {#task_object_merges}

Same as the [task_object_merge diff](#Merge) task, except you can provide multiple sidecars. The sidecars are applied in
the order defined in the task.

The task property “Sidecars” is a list of [Record object](#record-objects).
```
{
  "TaskType": "BatchMergesTask",
  "Task": {
    "Sidecars": [
      "<record>"
    ],
    "Reason": "company has new logos",
    "SubType": ""
  }
}
```

#### Publish {#task_object_publish}

Publishes the records. If the record is already published, the record will be `SKIPPED`. When strict validation is true,
more records will be skipped if the business logic does not allow the publication, i.e. when the record status
is `Draft.Invalid`.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| StrictValidation | boolean | If true, the publication validation will be more strict, i.e. does not allow the publication of records with `RecordStatus = Draft.Invalid`, resulting in more skipped records. | false | no |
```
{
  "TaskType": "BatchPublishTask",
  "Task": {
    "StrictValidation": false
  }
}
```

#### Diff {#task_object_diff}

Batch action to apply a diff to all records referred by the search request. The task property “Diff” is
a [Record diff](#record_diff_object).
```
{
  "TaskType": "BatchApplyDiffTask",
  "Task": {
    "Diff": "<RecordDiff>",
    "Reason": "Changed the tags to find the file",
    "SubType": ""
  }
}
```

#### Adopt {#task_object_adopt}

Batch action to used to adopt a parent for all records referred by the search request.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| ParentRecordId | String | The parent that all records need to adopt |  | yes |
| PreventForcedInheritance | boolean | Inheritance is normally forced when the record the adoption changes the top record, e.g. adoption leads to a different Classification or Series. This property disables the forced inheritance all together. | true | no |
| Reason | String | The reason why the task is being executed |  | no |
| SubType | String | The subevent type for the update event |  | no |
```
{
  "TaskType": "BatchAdoptTask",
  "Task": {
    "ParentRecordId": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
    "PreventForcedInheritance": true,
    "Reason": "Adopting new parent",
    "SubType": ""
  }
}
```

> Note: Records for which the user has no write rights will be skipped.

#### Delete {#task_object_delete}

Batch action used to delete in batch all records referred by the search request. The task has no properties. For
security reasons the following restrictions are in place:

- Query MUST contain only simple terms using the fields MediaObjectId, FragmentId, RecordId and fields related to
  reference codes
- Query features such as wildcards, ranges, OR, etc are forbidden
- Slices MUST be equal to 1

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| PreventCascade | boolean | If true, records deleted by the batch will not cascade if their own deletion policy is cascade. | true | no |
| Permanent | boolean | If true, permanently delete the record; only logically deleted records are allowed to be permanently deleted | false | no |
```
{
  "TaskType": "BatchDeleteTask",
  "Task": {
    "PreventCascade": false,
    "Permanent": false
  }
}
```

#### Restart failed jobs {#task_object_restart_failed_jobs}

Batch action used to restart all failed jobs linked to a record. The task has no properties.
```
{
  "TaskType": "RestartFailedJobsTask",
  "Task": {}
}
```

#### Touch {#touch_object}

Batch action used to update in batch all records referred by the search request. The task has no properties.
```
{
  "TaskType": "BatchTouchTask",
  "Task": {
    "Reason": "random update",
    "SubType": ""
  }
}
```

#### Retranscode {#retranscode_object}

Batch action used to retranscode in batch all records referred by the search request.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| ClusterGroups | Array of ClusterGroups | The cluster groups the file should be retranscoded to. | [“browse”, “browse_backup”] | yes |
```
{
  "TaskType": "BatchRetranscodeTask",
  "Task": {
    "ClusterGroups": [
      "tape_backup"
    ]
  }
}
```

#### Migrate date fields {#batches_migrate_date_fields}

Batch action is used to remove for a list of provided metadata field keys, those values which are not valid. Values
corresponding with old EXIF date are valid and hence not touched. Each invalid value is removed from the metadata field
and copied into another field having the same key but suffixed with `Legacy`. For each field the batch expects there to
be a corresponding indexed simple field with the same key suffixed by ‘Legacy’. For example when migrating the date
field `MyDateField` there MUST be another field `MyDateFieldLegacy`. Restrictions: each provided field must be pure
simple top field.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| FieldsToMigrate | JSON Array | List of top field (dotted) keys to migrate | [] | yes |
```
{
  "TaskType": "MigrateDateFieldsTask",
  "Task": {
    "FieldsToMigrate": [
      "MyDateField"
    ]
  }
}
```

#### Expression Templates {#task_object_expression_templates}

Batch action which provides the ability to determine the new metadata of the record through:

- the previous metadata of the record
- combinations of metadata fields
- conditions
- text operations

In order to achieve this, the metadata sidecar can now use a strict subset of Spring Expression Language (SpEL) to
perform more complex operations.  
You can put one or more expressions `#{...}` in the JSON. Inside an expression, you can reference the metadata
using `R(<Dotted key>)` or `record(<Dotted key>)`, for example `R('Descriptive.Title')` or `record('Descriptive.Title')`
.
See [Batch Metadata Expressions](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/3829858305/Batch+Metadata+Expressions)
for a more detailed explanation.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Templates | JsonObject[] | List of metadata sidecars containing expressions |  | yes |
```
{
  "TaskType": "BatchExpressionTemplatesTask",
  "Task": {
    "Templates": [
      {
        "MergeStrategies": {
          "Keywords": "OVERWRITE"
        },
        "Descriptive": {
          "Title": "#{R('Descriptive.Title').toUpperCase()}",
          "Description": "#{R('Descriptive.Title') + ': ' + R('Descriptive.Description')}",
          "Keywords": {
            "Keyword": "#{{R('Dynamic.CustomTag')}}"
          }
        },
        "Dynamic": {
          "Orientation": "#{R('Technical.Width') > R('Technical.Height') ? 'Horizontal' : 'Vertical'}",
          "AdditionalInformation": "My custom field"
        }
      }
    ]
  }
}
```

#### Export CSV {#export_csv_batch}

This batch action is used to export CSV with columns determined by a profile based on a filter query.
Once the batch completed, this CSV is uploaded as a new helper record.
After the record ingestion, an export is created for the user which started the batch.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| ExportFileName | String | Export file name. |  | yes |
| ProfileId | String | Profile ID. This profile determines fields used in CSV. |  | no |
| HeaderType | String | Header Type. Decides the how the header per field is resolved. Possible options are:  *DottedKey*  LongTranslation | DottedKey | no |
```
{
  "SearchRequest": {
    "Query": "+Internal.FragmentId:6e93c81441744335b788fbc3dca1b3992dccce8d32cc4633868322bcf35f33f5* +Internal.IsInIngestSpace:*",
    "SortField": "ArchiveDate",
    "SortDirection": "Desc"
  },
  "Slices": 1,
  "Propagate": false,
  "Label": "Export CSV",
  "TaskType": "BatchCSVTask",
  "Task": {
    "ExportFileName": "testFileName.csv",
    "ProfileId": "004de264-3d4c-46cb-b02d-b6641089638b",
    "HeaderType": "DottedKey"
  }
}
```

#### Record Diff {#record_diff_object}

The record diff is an object with as key a valid top field definition key and as value a diff containing the old and new
value.

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Key | String | The field definition key. |  | yes |
| Left | String | The old value of the field. |  | no |
| Right | String | The new value of the field. |  | no |

Remarks

- For a diff to be applied to a record, the record MUST have for the field in question the old value
- An empty value as old value means the field is created
- An empty value as new value means the field is removed
```
{
  "Descriptive.Title": {
    "Key": "Descriptive.Title",
    "Left": "The history of the main square",
    "Right": "The history of Wellermans square"
  },
  "Dynamic.Tags": {
    "Key": "Dynamic.Tags",
    "Left": "",
    "Right": "Agriculture,Farmers"
  }
}
```

#### Reharvest {#reharvest_batch}

This batch action is used to regenerate specific metadata fields that are typically automatically generated by AI.
For more information, see [reharvest](#reharvest).

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Features | List | A list of enum values specifying which (AI) features should be reharvested for the record. Possible values are `ExtractedMetadata`, `GenerativeMetadata`, `Ocr`, `Embeddings`. | depends on the active plugins | no |
| ProfileId | String | The AI profile that should be used, specifying the configuration to apply during the reharvest process. | id of profile with tag `Default.Ai` | no |
```
{
  "SearchRequest": {
    "Query": "+Internal.FragmentId:6e93c81441744335b788fbc3dca1b3992dccce8d32cc4633868322bcf35f33f5* +Internal.IsInIngestSpace:*",
    "SortField": "ArchiveDate",
    "SortDirection": "Desc"
  },
  "Slices": 1,
  "Propagate": false,
  "Label": "Reharvest records",
  "TaskType": "BatchReharvestTask",
  "Task": {
    "Features": [
      "GenerativeMetadata",
      "Ocr",
      "Embeddings",
      "Insights"
    ],
    "ProfileId": "214ac264-3d4a-48cb-b02d-b6641287655a"
  }
}
```

#### Convert to another main record type {#convert_record_batch}

This batch action is used to convert a record from its current main record type to another main record type.

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| TargetRecordType | String | The target main record type. It must have `RecordStructure` `Data`. | Dependent on the `DefaultRecordType` of the [Record scheme](#record_scheme_object) for the user’s organisation | yes |
```
{
  "SearchRequest": {
    "Query": "+Internal.FragmentId:6e93c81441744335b788fbc3dca1b3992dccce8d32cc4633868322bcf35f33f5* +Internal.IsInIngestSpace:*",
    "SortField": "ArchiveDate",
    "SortDirection": "Desc"
  },
  "Slices": 1,
  "Propagate": false,
  "Label": "Convert records to another main record type",
  "TaskType": "BatchConvertRecordTask",
  "Task": {
    "TargetRecordType": "Media"
  }
}
```

## Formats {#formats}

Formats can be used to manage supported file formats.

### Creating a format {#formats_post}

Create formats using a `POST` request containing a [Format](#format_object).
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/formats
```

#### Response

- `200` The created [Format](#format_object)
- `400` The request is not valid
- `403` User is not authorized
- `409` The format cannot be created

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_FORMATS’ function.

### Updating a format {#formats_update}

Updating a format can be done by performing a PUT-request with [Format](#format_object) as body to:
```
PUT https://archief.viaa.be/mediahaven-rest-api/v2/formats/:pronomId
```

#### Response

- `204` The format was updated
- `400` The request is not valid
- `403` User is not authorized
- `404` The format does not exist

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_FORMATS’ function.

### Deleting a format {#formats_delete}

A format can be deleted by performing a DELETE-request to:
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/formats/:pronomId
```

#### Response

- `204` The format was deleted
- `403` User is not authorized
- `404` The format could not be found
- `409` The format is used as target pronom for one or more transformations

### Getting all formats {#formats_get_all}

Retrieve a [Page](#page) of [Formats](#format_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/formats
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description |
| --- | --- |
| extension | Search for formats with a specific extension |
| allowed | Search for allowed or non-allowed formats |
| forPreservation | Search for formats where forPreservation is (non-)active |
| forAccess | Search for formats where forAccess is (non-)active |

#### Response

- `200` A [Page](#page) of [Formats](#format_object)
- `400` The request is not valid

#### Authorization functions

- Any authenticated user can access this resource.

### Getting a specific format {#formats_get_single}

Retrieve a single [Format](#format_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/formats/:pronomId
```

#### Response

- `200` Single [Format](#format_object)
- `404` The format could not be found

#### Authorization functions

- Any authenticated user can access this resource.

### Getting the transformations of specific format {#formats_get_single}

Retrieve A [Page](#page) of [Transformations](#transformation_object) for a format using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/formats/:pronomId/transformations
```

The standard [Page parameters](#page-filter) are available.

#### Response

- `200` A [Page](#page) of [Transformations](#transformation_object).
- `404` The format could not be found

#### Authorization functions

- Any authenticated user can access this resource.

### Linking a format with transformations {#formats_transformations_post}

Link a format with transformations using a `POST` request containing as body a JSON array of transformation IDs.
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/formats/:pronomId/transformations
```

#### Response

- `204` Success
- `400` The request is not valid
- `403` User is not authorized
- `404` The format or one of the transformations do not exist

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_FORMATS’ and ‘ADMIN_TRANSFORMATIONS’ function.

### Unlinking transformations from a format {#formats_transformations_post}

Unlink transformations from a format using a `DELETE` request containing as body a JSON array of transformation IDs.
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/formats/:pronomId/transformations
```

#### Response

- `204` Success
- `400` The request is not valid
- `403` User is not authorized
- `404` The format or one of the transformations do not exist

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_FORMATS’ and ‘ADMIN_TRANSFORMATIONS’ function.

### Format object {#format_object}

| Property | Type | Description | Default value |
| --- | --- | --- | --- |
| PronomId | String |  | Empty String |
| Name | String | The name of the format. | Empty String |
| Version | String | The version of the format. | Empty String |
| Allowed | Boolean | Is a file with this pronom allowed to be uploaded? | false |
| Extensions | String[] | The file extenstions for this format. | Empty String[] |
| ForPreservation | Boolean | The format is intended for preservation. | false |
| ForAccess | Boolean | The format is intended for accessing Records with this format. | false |

> Note: If you want to use the format as target pronom for a transformation, `Allowed` must be set to true and at least one of the two `ForPreservation` and `ForAccess` must be true.
```
{
  "PronomId": "fmt/1",
  "Name": "test format",
  "Version": "3",
  "Allowed": true,
  "Extensions": [
    "html",
    "htm"
  ],
  "ForPreservation": false,
  "ForAccess": true
}
```

## Transformations {#transformations}

Transformations defines the transformations that will be done between formats.

### Creating a transformation {#transformation_post}

Create transformations using a `POST` request containing a [Transformation](#transformation_object).
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/transformations
```

#### Response

- `200` The created [Transformation](#transformation_object)
- `400` The request is not valid
- `401` User is not authorized
- `409` The transformation cannot be created

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_TRANSFORMATIONS’ function.

### Updating a transformation {#transformations_update}

Updating a transformation can be done by performing a PUT-request with [Transformation](#transformation_object) as body
to:
```
PUT https://archief.viaa.be/mediahaven-rest-api/v2/transformations/:transformationId
```

#### Response

- `204` The transformation was updated
- `400` The request is not valid
- `401` User is not authorized
- `404` The transformation does not exist

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_TRANSFORMATIONS’ function.

### Deleting a transformation {#transformations_delete}

A transformation can be deleted by performing a DELETE-request to:
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/transformations/:transformationId
```

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_TRANSFORMATIONS’ function.

#### Response

- `204` The transformation was deleted
- `401` User is not authorized
- `404` The transformation could not be found

### Getting all transformations {#transformations_get_all}

Retrieve a [Page](#page) of [Transformations](#transformation_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/transformations
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description |
| --- | --- |
| name | Search for the transformation with this name |

#### Response

- `200` A [Page](#page) of [Transformations](#transformation_object)
- `400` The request is not valid

#### Authorization functions

- Any authenticated user can access this resource.

### Getting a specific transformation {#transformations_get_single}

Retrieve a single [Transformation](#transformation_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/transformations/:transformationId
```

#### Response

- `200` Single [Transformation](#transformation_object)
- `404` The transformation could not be found

#### Authorization functions

- Any authenticated user can access this resource.

### Getting source format(s) for a transformation {#transformation_get_formats}

A list of all source formats can be retrieved using a `GET` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/transformation/:transformationId/formats
```

The standard [Page parameters](#page-filter) are available.

#### Response

- `200` A [Page](#page) of [Formats](#format_object)
- `404` The transformation could not be found

#### Authorization functions

- Any authenticated user can access this resource.

### Adding source format(s) to a transformation {#transformation_add_formats}

One or more source formats can be added to a transformation by performing a `POST` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/transformation/:transformationId/formats
```

with an array with format ID(s)
```
[
  "<pronom of the format>",
  ...
]
```

> Note: Only 20 formats can be added within a single request.
> Note: Adding same format as FormatPronomId is not allowed.

#### Response

- `204` Formats were added.
- `400` No formats are in the list.
- `400` The number of formats is more than the number allowed within a single request.
- `403` The user does not have the required functions to call this method.
- `404` The transformation does not exist or one or more of the format ids do not exist.

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_TRANSFORMATIONS’ and ‘ADMIN_FORMATS’ function.

### Removing source formats(s) from a transformation {#transformation_delete_formats}

One or more source formats can be removed from a transformation by performing a `DELETE` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/transformations/:transformationId/formats
```

with an array with format ID(s)
```
[
  "<pronom of the format>",
  ...
]
```

> Note: Only 20 formats can be removed within a single request.

#### Response

- `204` Formats were removed.
- `400` No formats are in the list.
- `400` The number of formats is more than the number allowed within a single request.
- `403` The user does not have the required functions to call this method.
- `404` The transformation does not exist or one or more of the formats do not exist.

#### Authorization functions

- Using this endpoint requires the ‘ADMIN_TRANSFORMATIONS’ and ‘ADMIN_FORMATS’ function.

### Transformation object {#transformation_object}

| Property | Type | Description | Default value | Remarks |
| --- | --- | --- | --- | --- |
| Id | String |  | Empty String |  |
| Name | String | The name of the transformation. | Empty String |  |
| FormatPronomId | String | The target pronom for this transformation. | Empty String |  |
| ClusterGroups | String[] | The name of the cluster groups on which this transformation will be stored. | Empty String[] |  |
| Encoding.Width | Number | The width of the transformation ( -1 to scale image based on height, keeping aspect ratio). | null |  |
| Encoding.Height | Number | The height of the transformation ( -1 to scale image based on width, keeping aspect ratio). | null |  |
| Encoding.Container | String | Advanced option to configure the target file type. | null |  |
| Encoding.Transformer | String | Advanced option to configure the specific converter used. | null |  |
| Encoding.VideoBitrate | Number | The video bitrate of the transformation. (Bit/s) | null |  |
| Encoding.AudioBitrate | Number | The audio bitrate of the transformation. (Bit/s) | null |  |
| Encoding.AudioSamplerate | Number | The audio samplerate of the transformation. (Hz) | null |  |
| Encoding.AudioChannels | Number | The audio channels of the transformation. | null |  |
| Encoding.Cropping.Top | Number | The top value of the cropping feature. | null |  |
| Encoding.Cropping.Bottom | Number | The bottom value of the cropping feature. | null |  |
| Encoding.Cropping.Left | Number | The left value of the cropping feature. | null |  |
| Encoding.Cropping.Right | Number | The right value of the cropping feature. | null |  |
| Encoding.Watermark.Source | String | The source of the watermark applied by the transformation. | Empty String |  |
| Encoding.Watermark.Scale | Number | The scale of the watermark on the image. | 100 |  |
| Encoding.Watermark.Opacity | Number | The opacity of the watermark on the image. | 100 |  |
| Encoding.Watermark.Position | Enum (CENTER, TILED, NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST) | The position of the watermark on the image. | CENTER |  |
| Encoding.Keyframe.ThumbWidth | Number | The width of the generated keyframe ( -1 to scale image based on height, keeping aspect ratio). | null |  |
| Encoding.Keyframe.ThumbHeight | Number | The height of the generated keyframe ( -1 to scale image based on width, keeping aspect ratio). | null |  |
| Encoding.Rotate | Double(in degrees) | the value for the tilt of the image after transformation (max 359). | null |  |
| Encoding.Flip | Enum (HORIZONTAL, VERTICAL) | How the image will be flipped by the transformation. | null |  |
| Encoding.ColorSpace | Enum(sRGB, CMYK, RGB, LAB, AdobeRGB) | The color space of the transformation. | Empty String |  |
| Encoding.KeepColorSpace | Boolean | Whether the transformed file keeps the color space of the original. | False |  |
| ParentId | String | The id of the parent transformation. This is used for custom transformations linked to an [Ingest Configuration](#ingest_configuration) | null |
```
{
  "Id": "482f4cfa-d21e-4c0c-902b-e215f7587907",
  "Name": "test transformation",
  "TransformationPronomId": "fmt/1",
  "ClusterGroups": [
    "browse",
    "browse_backup"
  ],
  "Encoding": {
    "Width": 300,
    "Height": 150,
    "VideoBitRate": 3000000,
    "AudioBitRate": 150000,
    "AudioSampleRate": 48000,
    "AudioChannels": 2,
    "Cropping": {
      "Top": null,
      "Bottom": 5,
      "Left": null,
      "Right": 9
    },
    "Watermark": {
      "Source": "watermarkco",
      "Scale": 1,
      "Opacity": null,
      "Position": "CENTER"
    },
    "Rotate": 0.5,
    "Flip": "HORIZONTAL",
    "ColorSpace": "sRGB"
  },
  "ParentId": null
}
```

## Relation types {#relation_types}

This resource defines the possible types when setting the value of the `Relations` field.

> Note: Any authenticated user can set or remove system relations when creating/updating a [record](#metadata). This can have unintended consequences. Do so at your own risk.

### Getting all relation types {#relation_types_get}

Retrieve an array of [relation types](#relation_type_object) using a `GET` request
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/relation-types
```

#### Response

- `200` Ok. Body: list of [relation types](#relation_type_object)

#### Authorization functions

- Any authenticated user can access this resource

### Relation type object structure {#relation_type_object}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| RelationType | String | Name of the relation type. |  |  |
| Inverse | String | The RelationType of the inverse type. |  |  |
| IsSystem | boolean | Indicates whether the relation type is used by the system. |  |
```
{
  "RelationType": "IsChildOf",
  "Inverse": "IsParentOf",
  "IsSystem": true
}
```

## Validating a record {#record_validations}

A validation for [record metadata](#record-object) can be performed by sending a `POST` request containing
a [Validation request object](#record_validation_request) to :
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/validations
```

#### Response

- `200` Ok. Body: [Validation](#record_validation_object)

#### Authorization functions

- Any authenticated user can access this resource

### Validation request object {#record_validation_request}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Sidecar | [Sidecar](#sidecar_format) | The metadata you want to validate. | empty | yes |

Example:
```
{
  "Sidecar": {
    "Descriptive": {
      "Title": null
    }
  }
}
```

### Validation object {#record_validation_object}

| Property | Type | Description |
| --- | --- | --- |
| Valid | Boolean | Is the metadata valid or not. |
| Errors | Error[] | The list of validation errors. |
| Errors.Type | Enum | Type of the validation error (GLOBAL, REQUIRED_PARAMETER, INVALID_PARAMETER) |
| Errors.Code | String | A code specifying the precise error. See [below](#validation-error-codes) for a complete list. |
| Errors.Message | String | A message describing the error. |
| Errors.Field | String | The dotted key of the field. |
| Errors.Value | String | The erroneous value. |

Example:
```
{
  "Valid": false,
  "Errors": [
    {
      "Type": "REQUIRED_PARAMETER",
      "Code": "field.required",
      "Message": "Field Title is required and cannot be empty: Descriptive.Title: null",
      "Field": "Descriptive.Title",
      "Value": null
    }
  ]
}
```

### Validation error codes {#validation-error-codes}

List of error codes:

- field.required
- field.invalidkey
- field.invalidtype
- field.boolean.invalid
- field.date.invalid
- field.enum.invalid
- field.long.invalid
- field.relations.invalidtype
- field.relations.idnotfound
- field.timecode.invalid
- field.geocoordinate.invalidlatitude
- field.geocoordinate.invalidlongitude

## Saved filters {#filters}

### Introduction {#saved_filters}

A saved filter is a stored query you can re-execute a later time. These filters can be shared with any group from your
organisation you are member of.

User have read access to the following filters:

- Their own filters
- Filters having at least one group the user is member of
- If the user has the function `ADMIN_FILTERS`
    - All filters of the organisation of the user
    - Access to other organisations requires the function `ADMIN_VIEW_ALL_ORGANISATIONS`

User have write access to the following filters:

- Their own filters
- If the user has the function `ADMIN_FILTERS`
    - All filters of the organisation of the user
    - Access to other organisations requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`

Allowed user groups on create / update:

- The groups the user is member of
- If the user has the function `ADMIN_FILTERS`
    - The groups of the organisation of the filter
    - Groups from other organisations of the filter requires the `ADMIN_VIEW_ALL_ORGANISATIONS`

### Restrictions {#mediahaven-rest-api-manual-saved-filters-restrictions}

- The `Name` of a filter must not contain the special character `*`

### Creating a filter {#filters_post}

Create filters using a `POST` request containing a [Filter](#filter_object).
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/filters
```

#### Response

- `200` The created [Filter](#filter_object)
- `400` The request is not valid
- `401` User is not authorized
- `409` A filter with this name already exists for the organisation of the user

### Updating a filter {#filters_update}

Updating a filter can be done by performing a PUT-request with [Filter](#filter_object) as body to:
```
PUT https://archief.viaa.be/mediahaven-rest-api/v2/filters/:filterId
```

#### Response

- `204` The filter was updated
- `400` The request is not valid
- `401` User is not authorized
- `404` The filter does not exist
- `409` A filter with this name already exists for the organisation of the user

### Getting all filters {#filters_search}

Retrieve a [Page](#page) of [Filters](#filter_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/filters
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| name | The name of the filter. Wildcards \* are allowed. |  |
| createdBy | The user who created the filter |  |
| organisationId | The organisation the filter is part of | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| sort | Sort on one of the following fields (`Name`, `CreationDate`, `LastModifiedDate`) | Name |
| direction | The direction can be `asc`, `up`, `desc` or `down` | asc |

#### Response

- `200` A [Page](#page) of [Filters](#filter_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function

### Getting a specific filter {#filters_get_single}

Retrieve a single [Filter](#filter_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/filters/:filterId
```

#### Response

- `200` Single [Filter](#filter_object)
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the filter
- `404` The filter could not be found

### Deleting a filter {#filters_delete}

A filter can be deleted by performing a DELETE-request to:
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/filters/:filterId
```

#### Response

- `204` The filter was deleted
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the filter
- `404` The filter could not be found

### Filter object {#filter_object}

| Property | Type | Description | ReadOnly | Default Value |
| --- | --- | --- | --- | --- |
| Id | String | The identifier of the filter | Yes | Empty String |
| Name | String | The name of the filter |  | Empty String |
| Groups | String[] | Collection of group ids used by the filter |  | Empty String[] |
| CreatedBy | String | UserId of the creator of the filter | Yes | Id of the user |
| StructuredQuery | [StructuredQuery](#structured_query_object) | A structured representation of the query to save. |  |  |
| Query | String | DEPRECATED, use `StructuredQuery` instead. Query used to filter. |  | Empty String |
| OrganisationId | Number | Organisation id |  | Organisation of the user |
| CreationDate | Date (ISO8601) | Date the filter was created | Yes | Current time |
| LastModifiedDate | Date (ISO8601) | Date the filter was last updated | Yes | Current time |
| Context.IsEditable | Boolean | Field that indicates if the current user can edit the filter. | Yes |  |
| Context.IsExportable | Boolean | Field that indicates if the current user can delete the filter. | Yes |
```
{
  "Id": "482f4cfa-d21e-4c0c-902b-e215f7587907",
  "Name": "Test",
  "Groups": [
    "21",
    "1"
  ],
  "CreatedBy": "a12e9aea4z987a411da3d4",
  "Query": "+Title:test",
  "StructuredQuery": {
    "Global": [
      "Alice",
      "Bob",
      "Cedric"
    ],
    "AdvancedSearch": {
      "LogicalOperand": "And",
      "Groups": [
        {
          "LogicalOperand": "Or",
          "Terms": [
            {
              "DottedKey": "Descriptive.Keywords.Keyword",
              "Operand": "Include",
              "Values": [
                "A",
                "B",
                "C"
              ]
            },
            {
              "DottedKey": "Dynamic.CustomKeywords.Keyword",
              "Operand": "Include",
              "Values": [
                "A",
                "B",
                "C"
              ]
            }
          ]
        }
      ]
    }
  },
  "OrganisationId": 7,
  "CreationDate": "2021-03-26T09:38:34.188000Z",
  "Context": {
    "IsEditable": true,
    "IsDeletable": true
  }
}
```

## Structured query {#structured_query}

### Introduction {#mediahaven-rest-api-manual-structured-query-introduction}

Structured queries can be validated and parsed into flat queries that can be provided in turn to the `q` (query) and
`sq` (semantic query) parameters of various search endpoints.

### Parsing a structured query {#structured_query_post}

Parse a structured using a `POST` request containing a [structured query](#structured_query_object).
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/structured-query
```

#### Response

- `200` The [parsed structured query](#structured_query_post_response)
- `400` The request is not valid

### Structured query object {#structured_query_object}

The structured query provides search broken down into its individual constituents such that
selected facets and advanced search can be reconstructed later on.

| Property | Type | Description | Default Value |
| --- | --- | --- | --- |
| Global | String[] | List of free text search strings that supports [query syntax](#query-syntax). | [] |
| Semantic | String | Semantic search string using plain text only (no query syntax). Requires additional module. | Empty String |
| FullText | String | Full text search string using plain text only (no query syntax), also searches OCR-generated content. Requires additional module. | Empty String |
| AdvancedSearch | [AdvancedSearch](#sq_advanced_search_object) | The selected advanced search items | `null` |
| Facets | [Facet](#sq_facet_object)[] | The selected facets | [] |
| Predefined | String[] | Predefined filter queries that are always applied to refine search results based on specific conditions, regardless of other query parameters. | [] |

### Complete advanced search object {#sq_advanced_search_object}

The advanced search consists of a list of groups, surrounded by parentheses and joined by a logical AND/OR operation.
Within each advanced search group, there is a list of advanced search terms joined by another logical AND/OR operation.

| Property | Type | Description | Required | Default Value |
| --- | --- | --- | --- | --- |
| LogicalOperand | Enum (And, Or) | Logical operand to apply between all groups | Yes | And |
| Groups | [Group](#sq_advanced_search_group)[] | List of advanced search groups | Yes | Include |

### Advanced search group {#sq_advanced_search_group}

| Property | Type | Description | Required | Default Value |
| --- | --- | --- | --- | --- |
| LogicalOperand | Enum (And, Or) | Logical operand to apply between all terms. | Yes | Or |
| Terms | [Term](#sq_advanced_search_term)[] | List of selected values. An empty array is interpreted as a wildcard search. | No | [ ] |

### Advanced search term {#sq_advanced_search_term}

The advanced search term describes the search for a specific [field definition](#field_definitions) defined by its
dotted
key.

| Property | Type | Description | Required | Default Value |
| --- | --- | --- | --- | --- |
| DottedKey | String | The dotted key of the matching [field definition](#field_definitions). | Yes |  |
| Operand | Enum (Include, Exclude, Should) | Defines how a term is treated in the search. | Yes | Include |
| Values | String[] | List of selected values. An empty array is interpreted as a wildcard search. | No | [ ] |
| RangeValues | [RangeValue](#sq_range_value)[] | List of selected range values. Currently only supported for `DateFields`. | No | [ ] |

### Range value {#sq_range_value}

For date facets, the beginning and end of each selected date range is provided.

| Property | Type | Description | Required | Default Value |
| --- | --- | --- | --- | --- |
| Begin | String | Begin of the range | Yes |  |
| End | String | End of the range | Yes |  |
| IncludeBegin | Boolean | Whether the begin itself is included | No | True |
| IncludeEnd | Boolean | Whether the end itself is included | No | False |
| Gap | Enum | The size of the gap between begin and end. Possible values are `Year`, `Month` and `Day`. | No | `Year` |

#### Example

For example: `(FieldA:X OR FieldB:Y) AND -FieldC:[2024-01-08T00:00:00.000000Z TO 2024-07-01T19:00:00.000000Z]` will be
modelled as
```
{
  "LogicalOperand": "And",
  "Groups": [
    {
      "LogicalOperand": "Or",
      "Terms": [
        {
          "DottedKey": "FieldA",
          "Operand": "Include",
          "Values": [
            "X"
          ]
        },
        {
          "DottedKey": "FieldB",
          "Operand": "Include",
          "Values": [
            "Y"
          ]
        }
      ]
    },
    {
      "Terms": [
        {
          "DottedKey": "FieldC",
          "Operand": "Exclude",
          "RangeValues": [
            {
              "Begin": "2024-01-08T00:00:00.000000Z",
              "End": "2024-07-01T19:00:00.000000Z",
              "IncludeBegin": true,
              "IncludeEnd": true,
              "Gap": "Year"
            }
          ]
        }
      ]
    }
  ]
}
```

### Facet object {#sq_facet_object}

The facets are modelled as an ordered array of selected facets with each facet object providing the dotted
key and a list of selected buckets for that facet.

| Property | Type | Description | Required | Default Value |
| --- | --- | --- | --- | --- |
| LogicalOperand | Enum (And, Or) | Whether it concerns an AND- or OR-facet. | Yes | And |
| DottedKey | String | The dotted key of the matching [field definition](#field_definitions). | Yes |  |
| Buckets | [Bucket](#sq_facet_bucket_object)[] | List of selected buckets. | No\* | [ ] |
| RangeBuckets | [RangeBucket](#sq_facet_range_bucket_object)[] | List of selected ranges. Currently only supported for `DateFields`. | No\* | [ ] |

(\*) For date fields the property `RangeBuckets` MUST be provided, whereas for non-date fields the property `Buckets`
MUST be provided. Both
properties are mutually exclusive.

### Facet bucket object {#sq_facet_bucket_object}

For each facet one or more values, called “buckets” can be selected.

| Property | Type | Description | Required | Default Value |
| --- | --- | --- | --- | --- |
| Operand | Enum | The operand. Possible values: Include, Exclude | Yes | Include |
| Value | String | The selected value | Yes |

### Facet range bucket object {#sq_facet_range_bucket_object}

For date facets, the beginning and end of each selected date range is provided.

| Property | Type | Description | Required | Default Value |
| --- | --- | --- | --- | --- |
| Operand | Enum | The operand. Possible values: Include, Exclude | Yes | Include |
| RangeValue | [RangeValue](#sq_range_value) | The date range | Yes |

#### Example
```
[
  {
    "LogicalOperand": "Or",
    "DottedKey": "Descriptive.Keywords.Keyword",
    "Buckets": [
      {
        "Operand": "Include",
        "Value": "ValueA"
      },
      {
        "Operand": "Include",
        "Value": "ValueB"
      }
    ]
  },
  {
    "DottedKey": "Administrative.RecordType",
    "Buckets": [
      {
        "Operand": "Exclude",
        "Value": "Media"
      }
    ]
  },
  {
    "DottedKey": "Descriptive.CreationDate",
    "RangeBuckets": [
      {
        "RangeValue": {
          "Begin": "2024-01-01T00:00:00.000000Z",
          "End": "2025-01-01T00:00:00.000000Z",
          "IncludeBegin": true,
          "IncludeEnd": false,
          "Gap": "Year"
        }
      }
    ]
  }
]
```

### Parsed structured query object {#structured_query_post_response}

| Property | Type | Description |
| --- | --- | --- |
| Query | String | Suited for the `q` search parameter. |
| SemanticQuery | String | Suited for the `sq` search parameter. |
```
{
  "Query": "+Descriptive.Title:Alice +Descriptive.Keywords.Keyword:(Bob Cedric)",
  "SemanticQuery": "My semantic query"
}
```

## Reports {#reports}

### Introduction {#reports}

Reports contain an embed-url which is valid for a limited time.

#### Authorization functions

- Using this endpoint requires the `VIEW_REPORTS` function.
- Requesting data for other organisations requires the function `ADMIN_VIEW_ALL_ORGANISATIONS`:

### Getting all reports {#reports_search}

Retrieve a [Page](#page) of [Reports](#report_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/reports
```

| Query parameter | Type | Description | Default |
| --- | --- | --- | --- |
| collection | String | The collection the reports belong to. | empty |
| organisationId | String | The organisation for which the reports will contain data. | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: empty, otherwise the organisation of the user |
| onlyDefaults | Boolean | Only return the default reports | false |

Notes:
- When using the `collection` filter, the response will include:
- Reports belonging to the specified collection
- Additionally, any organisation specific reports stored in collections named `[Organisation] {organisationName}`, if
  such exist for the requested organisation(s).
- If the `collection` parameter is not provided, the system will check whether the active reporting module plugins (with category `BusinessIntelligence`) define a custom property named `default_collection`.
- If such a property exists, reports will be fetched for the specified `default_collection` value(s)
- Including any organisation specific reports from collections named `[Organisation] {organisationName}` for the
  relevant
  organisation(s).

#### Response

- `200` A [Page](#page) of [Reports](#report_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function(s)

### Getting a single report {#single_report}

Retrieve a single [Report](#report_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/reports/
```

| Query parameter | Type | Description | Default |
| --- | --- | --- | --- |
| organisationId | String | The organisation for which the report will contain data. | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: empty, otherwise the organisation of the user |

#### Response

- `200` Single [Report](#report_object)
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function(s)

### Report object {#report_object}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Id | Number | The identifier of the report |  |  |
| Label | String | The name of the report |  |  |
| Description | String | About the report |  |  |
| EmbedUrl | String | URL to embed this report in another web page. |  |  |
| Collection | String | The collection the report belongs to |  |  |
| Params | Param[] | List of additional query parameters that can be provided to the embed URL | Empty Param[] |

Example:
```
{
  "Id": 1,
  "Label": "Totale aantallen",
  "Description": "Totale aantallen van volume van downloads en bestanden in invoer of archief op dit moment. Delen van dit rapport kunnen data bevatten die tot twee dagen vertraging hebben.",
  "EmbedUrl": "https://dav-dev.digihaven.be/reporting/embed/dashboard/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNvdXJjZSI6eyJkYXNoYm9hcmQiOjF9LCJwYXJhbXMiOnsib3JnYW5pc2F0aWUiOiJEaWdpdGFhbCBBcmNoaWVmIFZsYWFuZGVyZW4iLCJvcmdhbmlzYXRpZV9fYWZrb3J0aW5nXyI6ImRhdiJ9fQ.9FZiCfuoz7t1bDsZ2QpQqH9lff3gIy6ujlyolmlBVOk#bordered=false&titled=false",
  "Collection": "Edepot",
  "Params": []
}
```

## Settings {#settings}

### Introduction {#settings_introduction}

Settings provide values for predefined settings definitions. Settings groups combine settings for a particular
service type (e.g. WEBSITE, ORGANISATION, etc) and have a human readable key. Both the Id and Key
uniquely identify a settings group. As some keys are in fact numbers, two settings groups can meet the request. In this case, the match with the same key takes precedence.
Settings can only be requested in the context of a settings group.

### Resources {#mediahaven-rest-api-manual-settings-resources}

#### Listing the settings groups {#get_settings_groups}

Get the list of settings groups using `GET`
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/settings
```

##### Response

- `200` An array of [Settings group(s)](#settings_group_object)
- `400` The request is not valid
- `403` User is not authorized to view settings

#### Authorization functions

- Requesting non-system settings groups requires the `VIEW_SYSTEM_SETTINGS` or `VIEW_ADMIN_SETTINGS` function,
  requesting system settings groups requires the `VIEW_SYSTEM_SETTINGS` function.
- Requesting settings groups from other organisations requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

#### Getting a single group {#get_settings_group}

Request a single [Complete settings group](#settings_group_object_complete) by its `Id` or `Key`.
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/settings/:settings-group-id-or-key
```

| Query parameter | Type | Description | Default Value |
| --- | --- | --- | --- |
| category | Enum CategoryType | Only return settings belonging to this category, see [CategoryType](#category_type) for possible values |  |
| privilege | Enum PrivilegeType | Only return settings belonging to this privilege, see [PrivilegeType](#privilege_type) for possible values |  |
| sort |  | Sort the settings one of the following fields (Key, Label) | Label |
| direction |  | The direction can be `asc`, `up`, `desc` or `down` | asc |
|  |

##### Response

- `200` A single [Complete settings group](#settings_group_object_complete)
- `400` The request is not valid
- `403` User is not authorized to view settings groups
- `404` Settings group does not exist or user has no access

#### Authorization functions

- Requesting non-system settings groups requires the `VIEW_ADMIN_SETTINGS` or `VIEW_SYSTEM_SETTINGS` function,
  requesting system settings groups requires the `VIEW_SYSTEM_SETTINGS` function.
- Requesting settings groups from other organisations requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

#### Getting a single setting of a settings group {#get_setting}

Request a single [Setting](#setting_object) by its `Key` (case insensitive)
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/settings/:settings-group-id-or-key/:setting-key
```

##### Response

- `200` A single [Setting](#setting_object)
- `400` The request is not valid
- `403` User is not authorized to view settings groups
- `404` Settings group or setting does not exist or user has no access

#### Authorization functions

- Requesting settings from a non-system settings group requires the `VIEW_ADMIN_SETTINGS` or `VIEW_SYSTEM_SETTINGS`
  function, requesting settings from a system settings group requires the `VIEW_SYSTEM_SETTINGS` function.
- Requesting settings from other organisations requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.
- Requesting settings with `SYSTEM` privilege requires the `VIEW_SYSTEM_SETTINGS` function.

#### Updating a single setting of a settings group {#update_setting}

Settings can be updated by performing a PUT-request with [UpdateSetting](#update_setting_object) as body to:
```
PUT https://archief.viaa.be/mediahaven-rest-api/v2/settings/:settings-group-id-or-key/:setting-key
```

##### Response

- `200` A single [Setting](#setting_object)
- `400` The request is not valid
- `403` User is not authorized to edit this setting
- `404` Settings group or setting does not exist

#### Authorization functions

- Updating settings from a non-system settings group requires the `EDIT_ADMIN_SETTINGS` or `EDIT_SYSTEM_SETTINGS`
  function, updating settings from a system settings group requires the `EDIT_SYSTEM_SETTINGS` function.
- Updating settings from other organisations requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.
- Updating settings with `SYSTEM` privilege requires the `EDIT_SYSTEM_SETTINGS` function.

### Objects {#mediahaven-rest-api-manual-settings-objects}

#### Settings group object {#settings_group_object}

| Property | Type | Description |
| --- | --- | --- |
| Id | String | Unique identifier of the settings group, will become a UUID in a future release (which is still a string) |
| Key | String | Unique name of the settings group |
| ServiceType | Enum ServiceType | One the types listed [below](#service_type) |
| System | Boolean | Whether the settings group is a system group. Depending on this value, other user functions are required to manage settings |

Example:
```
{
  "Id": "1",
  "Key": "dev",
  "ServiceType": "WEBSITE",
  "System": "false",
  "Settings": null
}
```

#### Complete settings group object {#settings_group_object_complete}

| Property | Type | Description |
| --- | --- | --- |
| Id | String | Unique identifier of the settings group, will become a UUID in a future release (which is still a string) |
| Key | String | Unique name of the settings group |
| ServiceType | Enum ServiceType | One of the types listed [below](#service_type) |
| System | Boolean | Whether the settings group is a system group. Depending on this value, other user functions are required to manage settings |
| Settings | [Settings](#setting_object)[] | List of [Settings](#setting_object) for this group |

Example:
```
{
  "Id": "9",
  "Key": "101",
  "ServiceType": "ORGANISATION",
  "System": "false",
  "Settings": [
    {
      "Key": "allow_duplicate_files",
      "Value": "FALSE",
      "Category": "ORGANISATION",
      "Privilege": "SYSTEM",
      "Label": "allow_duplicate_files",
      "Description": "Determines whether the same file can be uploaded multiple times.",
      "Type": "BOOLEAN",
      "Writeable": true,
      "Required": true
    }
  ]
}
```

#### Update setting object {#update_setting_object}

| Property | Type | Description | Required |
| --- | --- | --- | --- |
| Value | String | The new value for the setting. | yes |

Example:
```
{
  "Value": "The value of my setting is not 'The value of my setting'"
}
```

#### Enum ServiceType {#service_type}

- WEBSITE
- GLOBAL
- ORGANISATION
- UPLOADER

#### Setting object {#setting_object}

| Property | Type | Description |
| --- | --- | --- |
| Key | String | Unique key identifying the settings definition. |
| Value | String | Assigned value. |
| Category | Enum CategoryType | Subdivision of settings within a settings group, can be empty. See [below](#category_type) |
| Privilege | Enum PrivilegeType | One of the types listed [below](#privilege_type) |
| Label | String | Human readable name of the setting, in the locale of the user, if not defined, a fallback will be used |
| Description | String | Human readable description of the setting, in the locale of the user, if not defined, a fallback will be used |
| Type | Enum SettingsType | One of the types listed [below](#settings_type). |
| Writable | Boolean | Describes if the value can be changed. |
| Required | Boolean | The value MUST NOT be empty. |

> Note:
> If no translation for `Label` or `Description` is defined for the user’s locale, a fallback will be used, namely the first non-empty value from the following list:
> - The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
> - The translation for the ‘overall’ default locale `en_US`
> - Empty value

Example:
```
{
  "Key": "public_host",
  "Value": null,
  "Category": "INSTALLATION",
  "Privilege": "SYSTEM",
  "Label": "public_host",
  "Description": "De publieke host van de organisation",
  "Type": "STRING",
  "Writeable": true,
  "Required": true
}
```

#### Enum CategoryType {#category_type}

- UI
- FEATURES
- SEO

#### Enum PrivilegeType {#privilege_type}

- USER (deprecated, use ADMIN instead)
- ZETICON (deprecated, use SYSTEM instead)
- ADMIN
- SYSTEM

#### Enum SettingsType {#settings_type}

- INTEGER
- STRING
- BOOLEAN
- FLOAT
- XML
- JSON
- MEDIAOBJECT_ID
- FRAGMENT_ID
- UUID
- COLOR
- ARRAY
- EMAIL
- URL
- ENUM
- DATETIME
- MULTILINE
- FIELD_DEFINITION
- FIELD_DEFINITION_ARRAY
- ENUM_ARRAY
- PASSWORD

## Autocomplete {#autocomplete}

### Introduction {#autocomplete_introduction}

This endpoint provides automatic autocomplete for search queries. Autocomplete uses a data structure to look up terms.

Autocomplete is available for either:

- Preconfigured fields
    - `Global` (all global fields, i.e. the collection of field definitions marked as global)
- Searchable `SimpleFields` from the families (disallowed types are `BooleanField`, `DateField`, `LongField`, `FramesField` and `TextField`)
    - `Descriptive`
    - `Administrative`
    - `Technical`
    - `Dynamic`

> Terms are always matched in a case-insensitive manner, but are returned case-sensitive for all
> textual fields. For example consider following metadata “peer” and “Peer”. Autocompleting the input “pe” will return
> both “peer” and “Peer”
> as terms.
>
> The values of a field marked as global are split into tokens. For performance reasons, only 100 tokens per value are retained and included in the `Global` autocomplete field.

#### Authorization functions

- Any authenticated user can use this endpoint.

### Autocomplete object {#autocomplete_object}

| Property | Type | Description |
| --- | --- | --- |
| Term | String | The autocomplete value for this field |
| Score | Number | A weight representing how likely the term is a good fit |

#### example object {#autocomplete_object_ex}
```
{
  "Term": "foo bar",
  "Score": 2
}
```

### Autocomplete by field (GET) {#list_autocomplete}

Retrieve a list of [autocomplete objects](#autocomplete_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/autocomplete
```

| Query parameter | Type | Description | Default Value |
| --- | --- | --- | --- |
| input | String | The string you wish to autocomplete. Match in a case-insensitive manner. Match also on results which contain the provided `input` at any point. e.g. Zea in New-Zealand. |  |
| field | String | The field you wish to have autocomplete on (possible values: see introduction) | Global |
| nrOfResults | Number | The number of results that will be returned up to a maximum of 100 | 10 |
| indexWide | Boolean | If false, restrict to records that belong to the organisation of the user. | True |
| q | String | Restrict to autocomplete terms based on records matching the query, can be empty |

Autocomplete terms are derived from the `field` that is passed as parameter.

#### Response

- `200` Ok: A list of [autocomplete objects](#autocomplete_object)
- `400` Bad request
- `401` User is not authorized

### Autocomplete by field (POST) {#list_autocomplete_post}

Retrieve a list of [autocomplete objects](#autocomplete_object) using a `POST` request:
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/autocomplete

POST https://archief.viaa.be/mediahaven-rest-api/workflow/api/tasks/autocomplete
```

| Property | Type | Description | Default Value |
| --- | --- | --- | --- |
| Input | String | The string you wish to autocomplete. Match in a case-insensitive manner. Match also on results which contain the provided `input` at any point. e.g. Zea in New-Zealand. |  |
| Field | String | The field you wish to have autocomplete on (possible values: see introduction) | Global |
| NrOfResults | Number | The number of results that will be returned up to a maximum of 100 | 10 |
| IndexWide | Boolean | If false, restrict to records that belong to the organisation of the user. | True |
| Q | String | DEPRECATED, use `Search.StructuredQuery` instead. Restrict to terms based on records matching the query, can be empty |  |
| Search.StructuredQuery | [StructuredQuery](#structured_query_object) | Restrict to terms based on records matching the structured query, can be empty. |  |
| Search.OnlyCompletable | Boolean | `Only relevant when doing autocomplete on tasks` Whether to get values from all tasks, or only those you can complete | True |

Autocomplete terms are derived from the `field` that is passed as property.

#### Response

- `200` Ok: A list of [autocomplete objects](#autocomplete_object)
- `400` Bad request
- `401` User is not authorized

## Events {#metadata}

### Introduction {#mediahaven-rest-api-manual-events-introduction}

Events are point in time occurrences which change the state of various concepts in the installation. Examples include:

- User is created
- Record is modified
- Record is exported

The model of the syntax of the events follows the [Premis standard](https://www.loc.gov/standards/premis/index.html).
For now only events related to records are available.
For [data objects](#https://mediahaven.atlassian.net/wiki/x/PoBH8g) the events for the original representation (`VersionStatus` = `Head` or `Untracked`) are included by default.

### Getting a specific event for a record {#event_get_single}

Getting a specific event for a record is done by sending a GET-request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/events/:eventId
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

| Query parameter | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| translateIds | Boolean | If set to true, agentFormat can be used to translate the value of the Agent. | false | yes |
| agentFormat | String | If provided, defines how the `Agent` property of an [Agent](#event_agent_object) of type `MEDIAHAVEN_USER` should be formatted. | ${Login} | no |
| structures | array | Array of structures (Data, DataFlat, Representation, Classification, Intellectual) of records for which you want to receive the events | all | no |

The agentFormat parameter supports following variables:

- ${UserId}
- ${Login}
- ${LastName}
- ${FirstName}
- ${ExternalId}
- ${OrganisationName}
- ${OrganisationLongName}

#### Response

- `200` Ok. Body: [Event](#event_object)
- `400` One or more of the provided property values were not valid
- `404` The record or event was not found

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource

### Listing all events for a record {#event_get_all}

In order to get a complete list of all the events for a record, do a `GET` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/events/records/:id

https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/events
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

> Note: Requesting the events of a record by `/events/records/:id` is deprecated, use `/records/:id/events` instead.

| Query parameter | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| translateIds | Boolean | If set to true, agentFormat can be used to translate the value of the Agent. | false | yes |
| direction | String | Direction in which to sort the events by time, up or down. | up | no |
| agentFormat | String | If provided, defines how the `Agent` property of an [Agent](#event_agent_object) of type `MEDIAHAVEN_USER` should be formatted. | ${Login} | no |
| structures | array | Only applicable for [data objects](#https://mediahaven.atlassian.net/wiki/x/PoBH8g). Whether to include the data object, original representation or both. Possible values: Data, Representation. An empty array implies all. |  | no |

> Note: Supported variables for the agentFormat parameter can be found in the section [Getting a specific event for a record](#event_get_single)

#### Response

- `200` JSON Array of [Event](#event_object)
- `400` One or more of the provided property values were not valid
- `404` The record was not found

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource

### Creating an event for a record {#event_post}

To create a new event for a record you can send a `POST` request with [CreateEvent](#event_create_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/events
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

#### Response

- `201` The created [Event](#event_object)
- `400` One or more of the provided property values were not valid
- `404` The record was not found

#### Authorization functions

- Any authenticated user with write rights on the record can access this resource

### Event object {#event_object}

| Property | Type | Description | Default Value |
| --- | --- | --- | --- |
| IdentifierType | String | Fixed value MEDIAHAVEN_EVENT for events generated by Mediahaven. | MEDIAHAVEN_EVENT |
| Identifier | String | Unique identifier of the event, consider its format opaque as future releases will change the format to UUID. |  |
| RecordId | String | The record ID of the record for which the events are returned. |  |
| Concept | Concept | Fixed value of RECORDS for events generated by Mediahaven. | RECORDS |
| Type | Type | Type, see our [Confluence](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/1490485332/Events) for details. |  |
| SubType | Subtype | Sub type (can be empty) see our [Confluence](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/1490485332/Events) for details. |  |
| Date | Date (ISO8601) | Date of when the event occurred. |  |
| Comment | String | Comment describing the event. |  |
| Outcomes | [Outcome](#event_outcome_object)[] | List of outcomes with at least 1 item. |  |
| Agents | [Agent](#event_agent_object)[] | List of agents with at least 1 item. |  |
| Links | [Link](#event_link_object)[] | List of links with at least 1 item. |  |
| OriginalEventXml | String | The original premis event XML. |  |
| Difference | [Metadata change](#metadata_change_object)[] | List of metadata change objects. |  |
| CustomProperties | Map | A map of custom properties where both the keys and values are strings |  |
| Structure | Enum(Data, DataFlat, Representation, Classification, Intellectual) | Structure of the record for which the event was triggered |
```
{
  "IdentifierType": "MEDIAHAVEN_EVENT",
  "Identifier": "254946585",
  "RecordId": "419d8360046646ab9e844d14cb3dcd53513922ffc1ea44cc83d50432962404b5",
  "Concept": "RECORDS",
  "Type": "UPDATE",
  "SubType": "RELATIONS",
  "Date": "2020-07-13T16:30:01.901000Z",
  "Comment": "test",
  "Outcomes": [
    {
      "Outcome": "OK",
      "Note": "",
      "ExtensionXmls": [],
      "MdSecXmls": []
    }
  ],
  "Agents": [
    {
      "Type": "MEDIAHAVEN_USER",
      "Agent": "john.doe@example.com",
      "Roles": []
    }
  ],
  "Links": [
    {
      "Type": "MEDIAHAVEN_ID",
      "Link": "419d8360046646ab9e844d14cb3dcd53513922ffc1ea44cc83d50432962404b5b1ae7291afed4dbb925e4ef442c82e4c"
    }
  ],
  "OriginalEventXml": "",
  "Difference": [
    {
      "DottedKey": "Descriptive.Title",
      "ValueBefore": "My old title",
      "ValueAfter": "My new title"
    },
    {
      "DottedKey": "Descriptive.Description",
      "ValueBefore": "My old description",
      "ValueAfter": "My new description"
    }
  ],
  "CustomProperties": {
    "PropertyA": "myPropertyA",
    "PropertyB": "myPropertyB"
  }
}
```

### Event outcome object {#event_outcome_object}

| Property | Type | Description | Readonly | Default Value | Required |
| --- | --- | --- | --- | --- | --- |
| Outcome | String | Whether the event corresponds with success, the value is either OK or NOK. |  |  | yes |
| Note | String | Note describing the outcome. |  |  |  |
| ExtensionXmls | String[] | Property is defined by the Premis standard but not used by MediaHaven. | yes | empty list |  |
| MdSecXmls | String[] | Property is defined by the Premis standard but not used by MediaHaven. | yes | empty list |
```
{
  "Outcome": "OK",
  "Note": null,
  "ExtensionXmls": [],
  "MdSecXmls": []
}
```

### Event agent object {#event_agent_object}

| Property | Type | Description | Readonly | Default Value | Required |
| --- | --- | --- | --- | --- | --- |
| Type | String | Type of agent (`MEDIAHAVEN_SERVICE`, `MEDIAHAVEN_USER` OR a custom type) |  |  | yes |
| Agent | String | Value, being either a service name or user ID by default. |  |  | yes |
| Roles | String[] | Property is defined by the Premis standard but not used by MediaHaven. | yes | empty list |

> Note: On creation, only custom types are allowed
```
{
  "Type": "MEDIAHAVEN_USER",
  "Agent": "john.doe@example.com",
  "Roles": []
}
```

```
{
  "Type": "MEDIAHAVEN_SERVICE",
  "Agent": "WORKER_DAEMON",
  "Roles": []
}
```

### Event link object {#event_link_object}

| Property | Type | Description | Readonly | Default Value | Required |
| --- | --- | --- | --- | --- | --- |
| Type | String | Type of link, the value is either `MEDIAHAVEN_ID`, `EXTERNAL_ID` OR `EXTERNAL_EVENT_ID`. |  |  | yes |
| Link | String | Value of the link. |  |  | yes |

> Note: On creation, only type `EXTERNAL_EVENT_ID` is allowed
```
{
  "Type": "MEDIAHAVEN_ID",
  "Link": "419d8360046646ab9e844d14cb3dcd53513922ffc1ea44cc83d50432962404b5b1ae7291afed4dbb925e4ef442c82e4c"
}
```

```
{
  "Type": "EXTERNAL_ID",
  "Link": "n58cg1wz46"
}
```

### Metadata change object {#metadata_change_object}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| DottedKey | String | Dotted key. | no | yes |
| ValueBefore | String (JSON) | Attribute value before the change. | no | yes |
| ValueAfter | String (JSON) | Attribute value after the change. | no | yes |
```
{
  "DottedKey": "Descriptive.Description",
  "ValueBefore": "My old description",
  "ValueAfter": "My new description"
}
```

### Create event object {#event_create_object}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Type | Type | Type, see our [Confluence](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/1490485332/Events) for details. |  | yes |
| SubType | Subtype | Sub type, see our [Confluence](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/1490485332/Events) for details. |  |  |
| Comment | String | Comment describing the event. |  |  |
| Outcomes | [Outcome](#event_outcome_object)[] | List of outcomes with exactly 1 item. |  | yes |
| Date | Date (ISO8601) | Date of when the event occurred. | the current date |  |
| Agents | [Agent](#event_agent_object)[] | List of agents above the automatically generated agents. | empty list |  |
| Links | [Link](#event_link_object)[] | List of links above the automatically generated links. | empty list |  |
| CustomProperties | Json object whose properties are all strings | A map of custom properties where both the keys and values are strings. |  |
```
{
  "Type": "CUSTOM",
  "SubType": "TEST",
  "Comment": "test",
  "Outcomes": [
    {
      "Outcome": "OK",
      "Note": "note"
    }
  ],
  "Date": "2024-03-14T12:10:11.314000Z",
  "Agents": [
    {
      "Type": "USER_ID",
      "Agent": "123",
      "Roles": []
    }
  ],
  "Links": [
    {
      "Type": "EXTERNAL_EVENT_ID",
      "Link": "12412"
    }
  ],
  "CustomProperties": {
    "PropertyA": "myPropertyA",
    "PropertyB": "myPropertyB"
  }
}
```

## Jobs {#jobs}

Jobs gives an overview of all pending, active, completed and failed tasks.
It is also possible to restart failed jobs.

### Job object structure {#job_datamodel}

| Property | Type | Description |
| --- | --- | --- |
| Id | String (UUID) | A unique id. |
| Status | Enum | The status of the job. Possible values: Waiting, Processing, Completed, Rejected, Failed, Retrying. |
| Error | String | In case of failed jobs: A message describing the error that failed the job. |
| StackTrace | String | In case of failed jobs: Optionally, the stacktrace if available. If the user lacks the function `VIEW_BACKEND_MONITORING` this property is `null`. |
| TaskName | String | The name of the task of this job. |
| ExecutionId | String (UUID) | A unique execution id. |
| Zone | String | The zone of the worker daemon for this job. |
| UseLocalScope | Boolean | Use local scope for result parameters or not. |
| CreationDate | Date (ISO8601) | The date this job was created. |
| StartDate | Date (ISO8601) | The date when the status became Processing. |
| FinishDate | Date (ISO8601) | The date when the status became no longer Processing, null when status Waiting or Processing. |
| Attempts | Number | This property goes up by 1, every time the job is attempted, including retries and restarts. It is never reset to 0. There is are no business rules reasoning on the attempts. |
| RetryCount | Number | This property sets the number of retries counted until the job fails. It is reset to 0 each time the failed job is restarted. Each task defines the maximum number of retries within one run of a job (a run means, trying and retrying the job until it fails or completes). |
| Priority | Number | The priority in execution of this job (number between 0 and 15). |
| UserPriority | Enum | The user priority in execution of this job. Possible values: Background, Low, Normal, High. |
| RecordId | String | The ID of the record linked with this job. |
| OrganisationId | Number | The ID of the organisation of the record or process linked with this job. |
| BatchId | String (UUID) | The ID of the batch linked with this job. |
| ProcessInstanceId | String (UUID) | The ID of the process instance linked with this job. |
| ProcessName | String | The name of the process linked with this job. |
| WorkerDaemonId | String | The ID of the worker daemon which is processing the job currently. |
| Progress | Float | A number that represents the progress of the job: 0 (waiting), 0.1 (processing), 1.0 (success) |

Example:
```
{
  "Id": "89ba6941-92b3-44f1-af6c-99cd3bd17311",
  "Status": "Failed",
  "Error": "Python worker returned non-zero exit code: Error [708]: Cannot write to destination: ftp-active://dev-storage.mediahaven.com:None: 530 Login incorrect.",
  "Stacktrace": "",
  "TaskName": "EXPORTS_EXPIRE",
  "ExecutionId": "9e27dd91-8bbb-11eb-b30e-000c2982ac83",
  "Zone": "default",
  "UseLocalScope": true,
  "CreationDate": "2021-03-23T09:39:12.101000Z",
  "StartDate": "2021-03-23T09:40:11.121000Z",
  "FinishDate": "2021-03-23T09:41:05.002000Z",
  "RetryCount": 1,
  "Priority": 1,
  "UserPriority": "Normal",
  "RecordId": "d7b989e28e1b4300935ac049b5db44580566e5a28f64403e957312bb2f35eab1",
  "OrganisationId": 100,
  "BatchId": "6bae12aa-8f95-4897-a584-35b83343502c",
  "ProcessInstanceId": "3afe12aa-5f65-4d94-b144-25b83543542f",
  "ProcessName": "processName",
  "WorkerDaemonId": "",
  "Progress": 0.1
}
```

### Getting a job {#get_specific_job}

Getting a specific job is done by sending a `GET`-request to the following url.
```
https://archief.viaa.be/mediahaven-rest-api/v2/jobs/:id
```

#### Required functions {#jobs_functions}

The user requires the `VIEW_BACKEND_MONITORING` function to access this endpoint.

#### Response

- `401` User is not authorized
- `403` User does not have the correct function or has no access to the job
- `404` The job could not be found

### Restarting a job {#restart_job}

Restarting a failed job can be done by sending a `POST`-request to the following url:
```
https://archief.viaa.be/mediahaven-rest-api/v2/jobs/:id
```

with body
```
{
  "Action": "Restart"
}
```

#### Required functions {#jobs_functions}

The user requires the `EDIT_BACKEND_MONITORING` function to access this endpoint.

#### Response

- `204` The job was updated
- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to the job
- `404` The job could not be found

### Listing all jobs {#get_all_jobs}

The jobs can be retrieved using a `GET`-request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/jobs
```

This will return a list of the [jobs](#job_datamodel) in a paginated format.

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| TaskName | Search by task name. |  |
| RecordId | Search by record id. |  |
| Status | Search by status. |  |
| BatchId | Search by batch id. |

Sorting is also possible for this endpoint with the following query parameters:

| Query parameter | Description | Default |
| --- | --- | --- |
| SortField | The specific field you want to sort on. Possible values: Priority, Status, CreationDate, StartDate, FinishDate | Priority |
| SortDirection | The direction (Asc/Desc) for the SortField. | Desc |

#### Required functions {#jobs_functions}

The user requires the `VIEW_BACKEND_MONITORING` function to access this endpoint.

#### Response

- `400` The request is not valid
- `401` User is not authorized
- `403` User does not have the correct function or has no access to this endpoint

## Record jobs {#record-jobs}

### Get jobs linked to a record {#record-jobs-get}

To retrieve the jobs that are linked to a specific record, Send a `GET` request to following URL
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/jobs/:jobId
```

This will return a list of the [jobs](#job_datamodel) in a paginated format.

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| TaskName | Search by task name. |  |
| Status | Search by status. |  |
| BatchId | Search by batch id. |

Sorting is also possible for this endpoint with the following query parameters:

| Query parameter | Description | Default |
| --- | --- | --- |
| SortField | The specific field you want to sort on. Possible values: Priority, Status, CreationDate, StartDate, FinishDate | Priority |
| SortDirection | The direction (Asc/Desc) for the SortField. | Desc |

#### Authorization

- The user requires read rights on the record to list the jobs
- If the user has the function `VIEW_BACKEND_MONITORING` they can access the stacktrace of the failed jobs

### Restart failed jobs linked to a record and its (grand)children {#record-jobs-restart}

Certain jobs can be linked to a record. When a job fails, it will be saved in the database (jobs that are successful
will not be saved). These failed jobs can then be restarted.

To restart failed jobs that are linked to a specific record, Send a `POST` request to following url
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/jobs
```

With a body containing

- the action Restart
- a boolean indicating whether to also include the failed jobs of this record’s (grand)children
```
{
  "Action": "Restart",
  "IncludeChildren": "<boolean> optional, default false"
}
```

This will create a batch action that will try to restart all the failed jobs linked to this record and its
(grand)children (depending on IncludeChildren).

#### Response

- `202` if the batch action to restart the jobs is successfully created and has started
    - returns a [Batch](#batch_object)
- `400` if the specified record ID does not exist in the database
- `401` if user is not logged in/ authentication tokens are invalid
- `403` if the user does not have the required functions to access this endpoint

#### Authorization functions

The user needs the `EDIT_BACKEND_MONITORING` function to access this endpoint

## Calculating the diff between two records {#calculating_diff}

### Introduction {#diff_introduction}

An API user can retrieve the diff of the metadata of two records.
A diff is a list of fields whose value differs between two given records.
This provides the ability to easily compare the differences between these two records.

### Authorization functions {#mediahaven-rest-api-manual-calculating-the-diff-between-two-records-authorization-functions}

Any authenticated user can access this resource.

### Get the diff of two records {#diff_get}

Retrieve a [Diff](#diff_object) of two [Records](#record_object) using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/diff/:left/:right
```

Where `left` and `right` can both either be a `MediaObjectId`, `FragmentId` or `RecordId`

Additionally, the following query parameters can be used:

| Query parameter | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| include | String[] | A field that will be returned in the diff, given it differs between records. Can be repeated multiple times. Can not be combined with exclude. | Empty list | no |
| exclude | String[] | A field that will not be returned in the diff. Can be repeated multiple times. Can not be combined with include. | Ai.\* | no |

### Example {#mediahaven-rest-api-manual-calculating-the-diff-between-two-records-example}
```
{
  "Include": [
    "Descriptive.Title",
    "Descriptive.CreationDate",
    "Descriptive.Authors"
  ],
  "Exclude": [
    "Technical.Width",
    "Technical.Height"
  ]
}
```

##### Response

- `200` A [Record diff](#diff_object)
- `400` The request is not valid.
- `404` One or both records could not be found.

### Get the diff of two versions of a record {#diff_get_versions}

Retrieve a [Diff](#diff_object) of two [Versions](#versioning) of a record using a `GET` request:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/diff/:versioningId/versions/:left/:right
```

Where `left` and `right` can both either be:

- `head`
- `draft`
- a specific version number

Additionally, the following query parameters can be used:

| Query parameter | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| include | String[] | A field that will be returned in the diff, given it differs between records. Can be repeated multiple times. Can not be combined with exclude. | Empty list | no |
| exclude | String[] | A field that will not be returned in the diff. Can be repeated multiple times. Can not be combined with include. | Empty list | no |

##### Response

- `200` A [Record diff](#diff_object)
- `400` The request is not valid.
- `404` One or both versions could not be found.

### Calculate the diff of a record and sidecar metadata {#diff_post}

To retrieve the [Diff](#diff_object) of a [Record](#record_object) and sidecar metadata, you can use a `POST` request
using a [Diff request object](#diff-request):
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/diff/:left
```

Where `left` can both either be a `MediaObjectId`, `FragmentId` or `RecordId`.

| Query parameter | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Right | [Sidecar](#sidecar_format) | The (sidecar) metadata file, json or xml, that you want to upload. |  | yes |
| include | String[] | A field that will be returned in the diff, given it differs between records. Can be repeated multiple times. Can not be combined with exclude. | Empty list | no |
| exclude | String[] | A field that will not be returned in the diff. Can be repeated multiple times. Can not be combined with include. | Empty list | no |

##### Response

- `200` A [Record diff](#diff_object)
- `400` The request is not valid.
- `404` The record could not be found.

### Diff Request object {#diff-request}
```
{
  "Right": {
    "Descriptive": { "Title": "My title" }
  },
  "Include": [
    "Descriptive.Title",
    "Descriptive.CreationDate",
    "Descriptive.Authors"
  ],
  "Exclude": [
    "Technical.Width",
    "Technical.Height"
  ]
}
```

### Diff object structure {#diff_object}
```
[
  {
    "Key": "Descriptive.Title ",
    "Left": "My titlle",
    "Right": "My title"
  }
]
```

## Record inheritance {#record_inheritance}

This API endpoints provides for record the inheriting top metadata fields. Note that all inheriting
field definitions are included in the result, even if the record has no value for this field.

### Authorization {#mediahaven-rest-api-manual-record-inheritance-authorization}

- Read right on the record and its parent record

### Getting the inheritance fields for a record {#record_inheritance_get}
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/inheritance
```

Responds with a map of [record inheritance objects](#record-inheritance-object) with as keys the dotted key of the
inheriting fields.

#### Response

- `200` Map of [record inheritance objects](#record-inheritance-object)
- `404` The record itself or its parent was not found.

Example:
```
{
  "Descriptive.Title": {
    "DottedKey": "Descriptive.Title",
    "ParentValue": "Beautiful Lakes",
    "Value": "Lake Pukaki",
    "Inheritance": "Propagation",
    "Broken": true
  },
  "Descriptive.Keywords": {
    "DottedKey": "Descriptive.Keywords",
    "ParentValue": {
      "Keyword": [
        "Lake"
      ]
    },
    "Value": {
      "Keyword": [
        "Lake"
      ]
    },
    "Inheritance": "Propagation",
    "Broken": false
  }
}
```

### Record inheritance object {#record-inheritance-object}

| Property | Type | Description |
| --- | --- | --- |
| DottedKey | String | The dotted key of the [top field definition](#field_definitions_endpoint_single) |
| ParentValue | MetadataField (null, String or Object) | The value of metadata field on the parent; `null` if the record has no parent. |
| Value | MetadataField (String or Object) | The value of the metadata field |
| Inheritance | Enum (Creation, Propagation) | Type of inheritance for this field definition |
| Broken | boolean | Whether the inheritance has been broken by having a different value than the parent; `false` if the record has no parent. |

## Representations of a record {#representations}

### Querying the representations of a record {#representations_get}

See [documentation](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/3400007723/Record+Tree+Glossary) for
additional information about representations. The representations of a record can be fetched by performing a `GET`
request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/representations
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

The standard [Page parameters](#page-filter) are available.
Additionally, the following query parameters can be used:

| Query parameter | Type | Description | Default |
| --- | --- | --- | --- |
| original | boolean | Whether to include representations of type `Administrative.IsOriginal` field. | true |
| preservation | boolean | Whether to include representations of type `Administrative.IsPreservation` field. | true |
| access | boolean | Whether to include representations of type `Administrative.IsAccess` field. | true |
| fields | List | The fields that should be exposed in the result. Dotted keys are supported and `Score`,`Context` (Can be combined with profiles) | \* (all) |
| fieldsToExclude | List | The fields that should be excluded from the result (Can be combined with profiles and fields) | Ai.\* |
| profiles | List | The profiles for which the fields should be returned (Can be combined with fields and fieldsToExclude) |  |
| versioningStatus | List | Filters the descendants on their `Versioning.Status` field. Param can be repeated multiple times. If no status is specified, all versions are shown. |

#### Response

- `200` A [Page](#page) of [Record objects](#record-object).
- `400` One of the request parameters contains an invalid value.
- `404` The record itself was not found.

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource, only representations to which the user
  has read access to are returned.

### Creating a new representation {#representations_post}

A new representation can be created for a data record by performing a `POST` request to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/representations
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

Currently, only original representations can be created. The following options are available to upload a new original representation to the system:

- [Direct upload](#direct_file_upload)
- [Upload from url](#url_file_upload)
- [Resumable upload](#resumable_file_upload)

#### Parameters

The following parameters are available for all upload methods:

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| representationType | Enum (Original) | The type of representation to create. Currently, only `Original` is supported. |  | yes |
| metadata | [Sidecar](#sidecar_format) | Optional [Record object](#record-object) with metadata of the new representation, json or xml (always provide a content-type for this parameter). |  |  |
| priority | Enum (High, Normal, Low, Background) | Priority for processing the new representation. Setting this property requires the function `ADMIN_BACKEND_SERVICES`. | Normal |  |
| eventType | String | Sub event type for audit logging. |  |

#### Response

- `200` Ok: A [Record object](#record-object) of the new representation.
- `400` One of the request parameters contains an invalid value.
- `404` The record itself was not found.
- `409` Conflict with the current state of the record.

#### Authorization functions

- Any authenticated user with write rights on the record can access this resource.

## Record content {#record_content}

### Querying the content of a record (GET) {#querying_content_get}

The content of a record can be queried by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/content
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

The content includes the following:
- The immediate children of the record (first-level descendants), excluding representations.
- The pure fragments of the record.

The following query parameters can be used:

| Query parameter | Type | Description | Default Value | Maximum |
| --- | --- | --- | --- | --- |
| q | String | Free text search string that supports [query syntax](#query-syntax). |  |  |
| sq | String | Semantic search string using plain text only (no query syntax). Requires additional module. |  |  |
| ftq | String | Full text search string using plain text only (no query syntax), also searches OCR-generated content. Requires additional module. |  |  |
| minimumScore | Float | The minimum score for semantic query results | Dependent on plugin | 1.0 |
| fields | List | The fields that should be exposed in the result. Dotted keys are supported and `Score`,`Context` (Can be combined with profiles) | \* (all) |  |
| fieldsToExclude | List | The fields that should be excluded from the result (Can be combined with profiles and fields) | Ai.\* |  |
| profiles | List | The profiles for which the fields should be returned (Can be combined with fields and fieldsToExclude) |  |  |
| startIndex | Number | Used for pagination, search results will be returned starting from this index | 0 |  |
| nrOfResults | Number | The number of results that will be returned | 25 | 100 |

> Note: `Score` will be returned as part of the `Context` object.
> Note: Logically deleted fragments will also be returned. If you do not want this, you can include it in the query by searching for `Administrative.DeleteStatus:NotDeleted`.
> Note: Only children to which the user has read access are returned.

#### Response

- `200` A [Page](#page) of [Record objects](#record-object).
- `400` One of the request parameters contains an invalid value.
- `401` User is not authorized.
- `404` The record could not be found.

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource

### Querying the content of a record (POST) {#querying_content_post}

To search the content of a record using a `POST` request, the following endpoint can be used:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/content/search
```

Where `id` can be either a `MediaObjectId`, (main) `FragmentId` or `RecordId`.

The available properties are equivalent to [querying content using GET](#querying_content_get)

## Keyframes {#keyframes}

### Introduction {#keyframes_introduction}

A keyframe is a generated image preview.
Keyframes are generated for records that belong to one of the following media types:

- `Audio`
- `Video`
- `Document`
- `Newspaper`
- `Image` in instances where the image is multi layered, e.g. TIF
- `Media`
- `Representation`

A record can have multiple keyframes, depending on the size of the associated file.

### Getting keyframes for a video {#list_keyframes}

To fetch all keyframes for a video you can send a GET request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/keyframes
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

#### Response

- `200` List of [Keyframes](#keyframe_object)
- `403` User is not authorized
- `404` The record was not found
- `409` Record is being processed

### Keyframe object {#keyframe_object}

| Property | Type | Description |
| --- | --- | --- |
| AbsoluteTimeCode | ISO Timecode | Timecode relative to the start of the main fragment. |
| RelativeTimeCode | ISO Timecode | Timecode relative to the start of the main fragment. |
| ThumbnailImagePath | String | Url of the thumbnail image. |
| PreviewImagePath | String | Url of the previewimage. |

Example:
```
{
  "AbsoluteTimeCode": "00:00:08.880",
  "RelativeTimeCode": "00:00:08.880",
  "ThumbnailImagePath": "https://dev-storage-virtual.mediahaven.com/DEV/8a45012c1b654dc7a852d3fc45666ad4e8b566ff06144065bef209b9e087ffcf/keyframes-thumb/keyframes_1_1/keyframe1.jpg",
  "PreviewImagePath": "https://dev-storage-virtual.mediahaven.com/DEV/8a45012c1b654dc7a852d3fc45666ad4e8b566ff06144065bef209b9e087ffcf/keyframes/keyframes_1_1/keyframe1.jpg"
}
```

### Requesting a custom keyframe for fragment {#list_keyframes}

Custom keyframes are used for changing the preview of a fragment as linked by the URIs in the metadata fields

- `PathToKeyframe`
- `PathToKeyframeThumb`

Each video(fragment) can have exactly 1 custom keyframe. Custom keyframes have no impact on the regular keyframes
returned by [/keyframes](#list_keyframes)
which occur roughly every 10 seconds in the video.

To request a new custom keyframe for a video, send a `PUT` with body using content type
`application/json` and as model an [Create keyframe object](#request_keyframe_object).
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/custom-keyframe
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`. The record MUST be a video.

The call returns instantly while in the background the actual custom keyframe will be generated. While processing
the `BrowseStatus` of the record reverts to `in_progress`. The URLs `ThumbnailImagePath` and `PreviewImagePath` will
only resolve once the
`BrowseStatus` of the record becomes `completed` again.

#### Response

- `200` Single [Keyframe](#keyframe_object)
- `400` `KeyframeStart` is not within the interval `]0,<DurationInFrames>[`
- `400` `Type` of object is not `Video`
- `403` User is not authorized
- `404` The record was not found
- `409` Record is being processed (i.e. for another custom keyframe)

### Request custom keyframe object {#request_keyframe_object}

| Property | Type | Description |
| --- | --- | --- |
| KeyframeStart | integer | Expressed in frames (against a fictitious 25 fps) relative to the start of the main fragment. Causes to the metadata field `Descriptive.KeyframeStart` to acquire this value. |

Example:
```
{
  "KeyframeStart": 27
}
```

### Getting custom keyframe of a video {#get_custom_keyframe_video}

To get the custom keyframe for a video(fragment) you can send a GET request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/custom-keyframe
```

Where `id` can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

#### Response

- `200` [Keyframe](#keyframe_object)
- `403` User is not authorized
- `404` The record was not found or the record has no custom keyframe
- `409` Record is being processed

## Record fragments {#record_fragments}

### Introduction {#record_fragments_intro}

Fragments are specialized sub-objects with specific start and end coordinates, typically smaller than the entire (flat) data object.
The metadata field `MediaObjectId` is shared across all fragments. The flat data object itself is the main fragment, with its sub-objects being pure fragments.
More details can be found [here](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/4668391481/Fragments).

The endpoints described in this section are intended exclusively for pure fragments.

### Querying the fragments of a record (GET) {#querying_fragments_get}

The pure fragments of a data or flat data object can be queried by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/fragments
```

Where `id` can be either a `MediaObjectId`, (main) `FragmentId` or `RecordId`.

The following query parameters can be used:

| Query parameter | Type | Description | Default Value | Maximum |
| --- | --- | --- | --- | --- |
| q | String | Free text search string that supports [query syntax](#query-syntax). |  |  |
| sq | String | Semantic search string using plain text only (no query syntax). Requires additional module. |  |  |
| ftq | String | Full text search string using plain text only (no query syntax), also searches OCR-generated content. Requires additional module. |  |  |
| minimumScore | Float | The minimum score for semantic query results | Dependent on plugin | 1.0 |
| fields | List | The fields that should be exposed in the result. Dotted keys are supported and `Score`,`Context` (Can be combined with profiles) | \* (all) |  |
| profiles | List | The profiles for which the fields should be returned (Can be combined with fields) |  |  |
| startIndex | Number | used for pagination, search results will be returned starting from this index | 0 |  |
| nrOfResults | Number | the number of results that will be returned | 25 | 100 |

> Note: `Score` will be returned as part of the `Context` object
> Note: Logically deleted fragments will also be returned. If you do not want this, you can include it in the query by searching for `Administrative.DeleteStatus:NotDeleted`.

The available properties when sending a `POST` request are equivalent to the `GET` query parameters.

#### Response

- `200` A [Page](#page) of [Record objects](#record-object).
- `400` One of the request parameters contains an invalid value.
- `401` User is not authorized.
- `404` The record could not be found.

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource, only fragments to which the user
  has read access to are returned.

### Querying the fragments of a record (POST) {#querying_fragments_post}

To search pure fragments using a `POST` request, the following endpoint can be used:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/fragments/search
```

Where `id` can be either a `MediaObjectId`, (main) `FragmentId` or `RecordId`.

The available properties are equivalent to [querying fragments using GET](#querying_fragments_get)

### Getting a single fragment of a record {#fragments_get_all}

A single pure fragment of a data or flat data object can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/fragments/:fragmentId
```

The `recordId` can refer to a `MediaObjectId`, a (main) `FragmentId`, or a `RecordId`.
The `fragmentId` must specifically refer to the ID of a pure fragment.

Additionally, the following query parameters can be used:

| Query parameter | Type | Description | Default |
| --- | --- | --- | --- |
| fields | List | The fields that should be exposed in the result. Dotted keys are supported and `Score`,`Context` (Can be combined with profiles) | \* (all) |
| fieldsToExclude | List | The fields that should be excluded from the result (Can be combined with profiles and fields) | Ai.\* |
| profiles | List | The profiles for which the fields should be returned (Can be combined with fields and fieldsToExclude) |  |
| includeDeleted | Boolean | If true, also return the fragment if it has been logically deleted | false |

> Note: Pure fragments can only become logically deleted, by logically deleting the main fragment.

#### Response

- `200` A [Record object](#record-object).
- `401` User is not authorized.
- `404` The record or fragment could not be found.

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource, only fragments to which the user
  has read access to are returned.

### Creating a fragment {#fragments_create}

A pure fragment for a data or flat data object can be created by sending a `POST` request
with [Fragment options](#fragment_options_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/fragments
```

#### Response

- `200` Ok: A [Record object](#record-object) of the new fragment.
- `400` One of the request parameters contains an invalid value.
- `401` User is not authorized.
- `404` The record could not be found.
- `409` The record it still processing.

#### Authorization functions

- Any authenticated user with write rights on the record can access this resource.

### Updating a fragment {#fragments_update}

Updating a (pure) fragment can be done by performing a POST-request with [Fragment options](#fragment_options_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/fragments/:fragmentId
```

The `recordId` can refer to a `MediaObjectId`, a (main) `FragmentId`, or a `RecordId`.
The `fragmentId` must specifically refer to the ID of a pure fragment.

#### Response

- `200` Ok: [Record object](#record-object).
- `400` The request is not valid.
- `401` User is not authorized.
- `404` The record or fragment could not be found.

#### Authorization functions

- Any authenticated user with write rights on the record can access this resource.

### Deleting a fragment {#fragments_delete}

A pure fragment can be deleted by performing a `DELETE` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/fragments/:fragmentId
```

The `recordId` can refer to a `MediaObjectId`, a (main) `FragmentId`, or a `RecordId`.
The `fragmentId` must specifically refer to the ID of a pure fragment.

Extra parameters can be provided via an optional [request body](#delete_fragment_object).

Notes:
- Deletes are idem potent. This means that when the same request is repeated multiple times, no error will be thrown.
- Unlike with main fragments, the deletion of a pure fragment is instantly permanent and therefore irreversible (`DeleteStatus = PermanentlyDeleted`).
- Use the [delete record](#deleting) endpoint to remove main fragments.

#### Response

- `204` The fragment was deleted.
- `401` User is not authorized.
- `404` The record or fragment could not be found.

#### Authorization functions

- Any authenticated user with delete rights on the record can access this resource.

### Fragment options object structure {#fragment_options_object}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| FragmentStartFrames | Number | The start offset of the pure fragment, expressed in units such frames, pages, layers, etc. |  | yes if FragmentStartTimeCode not defined |
| FragmentEndFrames | Number | The end offset of the pure fragment, expressed in units such frames, pages, layers, etc. The end is not included, hence it forms a half-open interval, mathematically expressed as [start, end[. |  | yes if FragmentEndTimeCode not defined |
| FragmentStartTimeCode | String | The same as FragmentStartFrames but expressed in timecode units. |  | yes if FragmentStartFrames not defined |
| FragmentEndTimeCode | String | The same as FragmentEndFrames but expressed in timecode units. |  | yes if FragmentEndFrames not defined |
| Metadata | [Sidecar](#sidecar_format) | The metadata you want to add. |  | no |
| Title | String | The title of the fragment that will be created. | title of the main fragment | no |
| Reason | String | The reason why the fragment is being created / updated (for audit logging). |  | no |
| EventType | String | The event subtype generated when the fragment is created / updated (for audit logging). |  | no |

Note: You can provide the (relative) in- and out-points, specifying the boundaries either on a Frame basis or a TimeCode basis. Mixing formats is not allowed.

Example Frame basis:
```
{
  "FragmentStartFrames": "2",
  "FragmentEndFrames": "50",
  "Metadata": {
    "Descriptive": {
      "Description": "Description of new fragment"
    }
  },
  "Title": "My new fragment",
  "Reason": "Creating new fragment",
  "EventType": ""
}
```

Example TimeCode basis:
```
{
  "FragmentStartTimeCode": "00:00:10.000",
  "FragmentEndTimeCode": "00:00:20.000",
  "Metadata": {
    "Descriptive": {
      "Description": "Description of new fragment"
    }
  },
  "Title": "My new fragment",
  "Reason": "Creating new fragment",
  "EventType": ""
}
```

### Delete fragment object structure {#delete_fragment_object}

| Property | Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| Reason | String | The reason why the fragment is deleted | empty string | no |
| EventType | String | A custom Subtype for the delete event | empty string | no |
```
{
  "Reason": "deprecated fragment",
  "EventType": "OBSOLETE"
}
```

## Record children {#children}

### Querying the children of a record {#generate_browses}

The children of a record can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/children
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| recordStatus | Filters the descendants on their `Administrative.RecordStatus` field. Param can be repeated multiple times. |  |
| level | The level of descendants to fetch. Possible values are: `Children`, `GrandChildren`, `All`. Note that `GrandChildren` only returns the direct grandchildren of the parent record. It doesn’t return the direct children or any other descendants. | Children |
| recordStructure | The structure of descendants to fetch. Possible values are: `Data`, `DataFlat`, `Intellectual`, `Representation`, `Classification`. Param can be repeated multiple times. |  |
| publicOnly | If true, only the descendants which are publicly accessible are returned. | false |
| versioningStatus | Filters the descendants on their `Versioning.Status` field. Param can be repeated multiple times. If no status is specified, all versions are shown. |

#### Response

- `200` Ok: A list of record ids. This can also include records the user does not have read permissions for.
- `400` One of the request parameters contains an invalid value.
- `404` The record was not found.

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource

### Default child sorting {#default_child_sorting}

You can save the default child sorting by passing the option ‘childOrderFields’ to the record endpoint when saving a
record. This option will store the sort field and order in the metadata, which can be used by the client to set the
sorting when displaying the children of that record. See also [edit record](#edit_formdata_parameters) for more info on
how to store the default sorting.

The ‘ChildOrderFields.Field’ has a property ‘DottedKey’ that references another field-definition (this field-definition
should be sortable) and a ‘Direction’ which holds the direction (‘Asc’, ‘Desc’)

Example (partial):
```
"ChildOrderFields": {
"Field": [
{
"DottedKey": "Descriptive.Title",
"Direction": "Asc"
}
]
}
```

Note: The default sorting order is not applied automatically, it is just available as metadata so the client can use it.

## Record rejections {#record_rejections}

### List the rejections of a record and its (grand)children {#list_record_rejections}

The rejections of a record, its (grand)children and (in case of a SIP) its contained records can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/rejections
```

Where id can be either a `MediaObjectId`, `FragmentId` or `RecordId`.

> Note: When requesting the rejections of a data record, only the `Head` version of the original representation is shown if it is versioned.

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| filterUpwardPropagation | Should the result filter out the upward propagated rejections | true |
| includeCandidates | Should the result include rejections of candidate children | false |
| versioningStatus | Filters the descendants on their `Versioning.Status` field. Param can be repeated multiple times. | depends on the `Versioning.Status` of the requested record |

Note: The default for `versioningStatus` is determined as follows:
- If the version status of the requested record is `Head` or `Untracked`, then both statuses are used as the default.
- For any other status (e.g., `Draft`, `Tail`, `Rejected`), the default matches the versioning status of the requested record.

#### Response

- `200` A [Page](#page) of [Rejections](#rejections_object)
- `401` User is not authorized.
- `400` One or more of the provided property values were not valid.
- `404` The record was not found.

#### Authorization functions

- Any authenticated user with read rights on the record can access this resource

### Get number of records containing rejections for a record {#count_record_rejections}

To get the total number of records containing rejections for a record, do a `HEAD` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/records/:id/rejections
```

The response will contain a header element with the name `Result-Count`. The total count can include the record itself and its (grand)children.

#### Response

- `200` Number of results.
- `401` User is not authorized.
- `404` The record was not found.

### Rejections object structure {#rejections_object}

| Property | Type | Description |
| --- | --- | --- |
| RecordId | String (UUID) | The record id to which the rejections apply (can be the record itself, a child or grandchild) |
| Breadcrumb | String | Breadcrumb trail consisting of the titles of the requested record to the record to which the rejections apply |
| Rejections | List | List of rejections |
| Rejections > Reason | String | A technical key for the reason of the rejection |
| Rejections > Motivation | String | A human readable motivation for the rejection (language independent). Can contain technical information |
| Rejections > Description | String | The description of the rejection that matches with the current user locale |
| Rejections > Descriptions > Lang | String | The locale for the description of the rejection |
| Rejections > Descriptions > Value | String | The description for the given locale, if not defined, a fallback will be used |
| Rejections > Date | Date (ISO8601) | The date when the rejection occurred |
| Rejections > User | String | The user who rejected the record |
| Rejections > Row | Number | The row in the metadata file of the SIP that contains the error (Only present when applicable) |
| Rejections > Path | String | The path in the metadata file of the SIP that contains the error (Only present in when applicable) |
| Rejections > Field | String | Dotted key of the field |
| Rejections > Value | String | Value of the field |

> Note: `Descriptions` contains translations for each supported locale. If no translation is defined for a specific locale, a fallback will be used, namely the first non-empty value from the following list:
>  - The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
>  - The translation for the ‘overall’ default locale `en_US`
>  - The value of the `Motivation` field
```
{
  "RecordId": "0863d8751eda4dd09f4b2fcd5f637489c41f475410525a02923f5290c5788758",
  "Breadcrumb": "Title A > Title B > Title C",
  "Rejections": [
    {
      "Reason": "NOT_BLANK",
      "Motivation": "Name can not be blank",
      "Description": "Naam is verplicht",
      "Descriptions": [
        {
          "Lang": "en_US",
          "Value": "Name is required"
        },
        {
          "Lang": "nl_BE",
          "Value": "Naam is verplicht"
        }
      ],
      "Date": "2023-01-16T08:20:36.000000Z",
      "User": "system@installation"
    },
    {
      "Reason": "METADATA_FIELD_INVALID_DATE",
      "Motivation": "'2023-01-14' is not a valid date, use ISO8601 as date format",
      "Description": "Datum is niet geldig",
      "Descriptions": [
        {
          "Lang": "en_US",
          "Value": "Date is not valid"
        },
        {
          "Lang": "nl_BE",
          "Value": "Datum is niet geldig"
        }
      ],
      "Date": "2023-01-16T08:28:34.000000Z",
      "User": "system@installation"
    }
  ]
}
```

## Indices {#indices}

Objects are stored are persisted in the database.
However, when searching for objects a search platform, namely Apache SOLR, is used to offer [search for objects](#search-for-media-objects).

> The search platform is divided in a number of indices in two distinct manners:
> 1. Shared index: One single index for all organisations
> 2. Non-shared index: One index per organisation

“Shared index” is used for installations where some users can search over multiple organisations. The setting `shared_index` defines whether the installation uses a shared index.

### Authorization functions {#mediahaven-rest-api-manual-indices-authorization-functions}

- All calls to this endpoint require the function `MANAGE_INDICES`
- `GET` calls to this endpoint require the function `ADMIN_VIEW_ALL_ORGANISATIONS`.
- Other calls to this endpoint require the function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Creating an index {#create_index}

An index can be created by sending a POST request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/indices
```

with body using content type `application/json` and as model an [Create index object](#create_index_data_model).

If the index does not yet exist, the index will be created using the following name as index name:
*name of the organisation when `shared_index` = false* name of the primary organisation when `shared_index` = true

This index is registered in the database and created in the search framework SOLR.
If the index was removed from the search framework, you can repeat this `POST` ensure the index is created again
in the search framework SOLR.

#### Response

- `201` Created: [index object](#index_data_model)
- `400` Invalid request
- `403` User is not authorized
- `404` Organisation does not exist

### Retrieving a list of indices {#get_indices}

A general overview of indices can be retrieved by sending a `GET` request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/indices
```

The standard [Page parameters](#page-filter) are available on this endpoint.

#### Response

- `200` OK. A [Page](#page) of [Index objects](#index_data_model)

### Fetch a specific index {#get_index}

Specific index can be retrieved by sending a GET request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/indices/:name
```

where `:name` refers to the Name property of the index.

#### Response

- `200` OK: An [Index object](#index_data_model)
- `403` User is not authorized
- `404` Not found

### Reindexing {#start_reindex}

Reindexing causes all non permanently deleted objects to be sent to the indexes in question.
A number of reindex variants are available:

1. Reindex
    1. Sent all objects to the existing index
    2. The old metadata remains available while the reindex is running
    3. Includes reindex of thesauri
2. Rebuild
    1. Create a temporary index in background
    2. Sent all objects to the temporary index
    3. Replace the index with the temporary index
    4. Includes export and reindex of thesauri

#### Reindex a specific reindex {#start_reindex_one_index}

To reindex an index, send a PUT request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/indices/:name
```

where `:name` refers to the Name property of the index and with body in format `application/json`.

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Action | Enum(Reindex,Rebuild) | The action to perform |  | yes |
| Slices | int | Number of slices per index fetching from the database | 1 | no |

> Higher values for slices decrease the reindex time at cost of higher database load and more queue space consumption.
> When reindexing multiple indices the best value is 1.
> When reindexing a single (shared) index, a good number is 4.
>
> ```
> {
>   "Action": "Reindex",
>   "Slices": 1
> }
> ```

##### Response

- `202` Accept
- `400` Invalid request:
    - Unknown action
    - Slices is not in range [1,128[
- `403` User is not authorized
- `409` Conflict: a reindex is already in progress

#### Reindex all indices {#start_reindex_all_index}

To reindex *all* indices, send a PUT request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/indices
```

with body in format `application/json` and same properties as for a [specific index](#start_reindex_one_index).

##### Response

- `202` Accept
- `400` Invalid request:
    - Unknown action
    - Slices is not in range [1,128[
- `403` User is not authorized
- `409` Conflict: a reindex is already in progress for at least one of the indices

### Create index object model {#create_index_data_model}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| Organisation | String | Name of the organisation for which to create the index |  | Yes |
| Shared | Boolean | `Deprecated property, might be removed in the future. Installation setting shared_index is used instead.` If set to true, the organisation will use the index of the primary organisation. | True | Yes |

### Index object model {#index_data_model}

| Property | Type | Description | Default value | Required | Read-only |
| --- | --- | --- | --- | --- | --- |
| Name | String | Unique name of the index. |  | No | No |
| Organisations | Number array | The ids of the [organisations](#organisations) |  | Yes | Yes |
| LastReindex.StartTime | Date (ISO8601) | Time the last reindex was started |  |  | Yes |
| LastReindex.FinishTime | Date (ISO8601) | Time the last reindex was finished |  |  | Yes |
| LastReindex.BatchId | UUID | Id of the [batch](#batches) linked to this reindex. |  |  | Yes |
| LastReindex.Status | String | Status of the reindex: Waiting, Processing, ProcessingInIndex, Completed, Failed |  |  | Yes |

### Reindex status {#index_status}

| Status | Meaning |
| --- | --- |
| Waiting | Reindex requested but the workflow/batch has yet to be created |
| Processing | Reindex has an active batch |
| ProcessingInIndex | Reindex batch has been completed, but the index is still processing the generated messages |
| Completed | Reindex has been completed without any errors |
| Failed | Reindex has been completed but the batch has at least 1 error for a record |
```
{
  "Name": "beeldbank-mgmt",
  "Organisations": [
    100,
    105
  ],
  "LastReindex": {
    "StartTime": "2021-03-23T09:39:12.101000Z",
    "FinishTime": "2022-03-23T09:39:12.101000Z",
    "BatchId": "21f80c6d-52b2-56d4-9db5-029660f21512",
    "Status": "Completed"
  }
}
```

## Reindexes {#reindex}

Reindex operations can be tracked via this api

### Authorization functions {#mediahaven-rest-api-manual-reindexes-authorization-functions}

- All calls to this endpoint require the function `MANAGE_INDICES`
- `GET` calls to this endpoint require the function `ADMIN_VIEW_ALL_ORGANISATIONS`.
- Other calls to this endpoint require the function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Start a reindex {#start_reindex}

A reindex can be started by sending a POST request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/reindexes
```

with body using content type `application/json` and as model a [Reindex object](#create_reindex_data_model).

Sending a request without `IndexName` will cause a reindex for all organisations.

Reindexing causes all non permanently deleted objects to be sent to the indexes in question.
A number of reindex variants are available:

1. Reindex
    1. Sent all objects to the existing index
    2. The old metadata remains available while the reindex is running
    3. Includes reindex of thesauri
2. Rebuild
    1. Clear existing index
    2. Includes export and reindex of thesauri
    3. Sent all objects to the index

#### Response

- `200` Successfully created
- `400` Invalid request:
    - Unknown type
    - Slices is not in range [1,128[
- `403` User is not authorized
- `409` Conflict: a reindex is already in progress

### Retrieve all reindex operations {#get_reindex_all}

A general overview of all reindex operations can be retrieved by sending a `GET` request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/reindexes
```

The standard [Page parameters](#page-filter) are available on this endpoint.

Additionally, the following query parameters can be used:

| Query parameter | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| indexName | String | Filter by index name. |  | no |
| parentOnly | Boolean | Whether to return only reindex operations without parent. | true | no |
| activeOnly | Boolean | Whether to return only reindex operations which are not finished yet. | false | no |

#### Response

- `200` OK. A [Page](#page) of [Reindex objects](#reindex_data_model)

### Retrieve a single reindex operation {#get_reindex_single}

A specific reindex operation can be retrieved by sending a GET request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/reindexes/:id
```

where `:id` refers to the Id property of the reindex.

#### Response

- `200` OK: A [Reindex object](#reindex_data_model)
- `403` User is not authorized
- `404` Not found

### Cancel a reindex {#cancel_reindex}

Cancelling a reindex can be done by sending a DELETE request to
```
https://archief.viaa.be/mediahaven-rest-api/v2/reindexes/:id
```

where `:id` refers to the Id property of the reindex.

#### Response

- `200` OK: A [Reindex object](#reindex_data_model)
- `400` Reindex is not in a cancellable state
- `403` User is not authorized
- `404` Not found
- `409` Reindex is being cancelled

### Create reindex object model {#create_reindex_data_model}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| IndexName | String | Name of index for which to start the reindex |  | No |
| Type | Enum(Reindex,Rebuild) | The type of reindex | Reindex | Yes |
| Slices | Number | Number of slices per index fetching from the database | 1 | no |

> Higher values for slices decrease the reindex time at cost of higher database load and more queue space consumption.
>
> When reindexing multiple indices the best value is 1.
>
> When reindexing a single (shared) index, a good number is 4.

#### Response

- `200` OK: A [Reindex object](#reindex_data_model)
- `400` Invalid parameters provided
- `403` User is not authorized
- `404` Not found
- `409` A reindex is already active

### Reindex object model {#reindex_data_model}

| Property | Type | Description |
| --- | --- | --- |
| Id | String | Unique id of the reindex |
| IndexName | String | Name of the index for which the reindex is triggered |
| StartTime | Date (ISO8601) | Time the reindex was started |
| FinishTime | Date (ISO8601) | Time the reindex was finished |
| BatchId | UUID | Id of the [batch](#batches) linked to this reindex. |
| FieldChanges | Boolean | True if field changes are applied in this reindex |
| Status | Reindex status | [Status](#reindex_status) of the reindex |

### Reindex status {#reindex_status}

| Status | Meaning |
| --- | --- |
| Waiting | Reindex requested but the workflow/batch has yet to be created |
| Processing | Reindex has an active batch |
| ProcessingInIndex | Reindex batch has been completed, but the index is still processing the generated messages |
| Completed | Reindex has been completed without any errors |
| Cancelling | Reindex is being cancelled |
| Cancelled | Reindex has been cancelled |
| Failed | Reindex has been completed but the batch has at least 1 error for a record |
```
{
  "Id": "123",
  "IndexName": "index", 
  "StartTime": "2021-03-23T09:39:12.101000Z", 
  "FinishTime": "2022-03-23T09:39:12.101000Z", 
  "BatchId": "21f80c6d-52b2-56d4-9db5-029660f21512", 
  "FieldChanges": false, 
  "Status": "Completed"
}
```

### Paged result {#page}

| Property | Type | Description |
| --- | --- | --- |
| Results | List of objects | List of results. |
| NrOfResults | Number | The amount of results in the ‘Results’ list. |
| StartIndex | Number | The startIndex of the results in the total list of results. |
| TotalNrOfResults | Number | The total amount of results. |

Example:
```
{
  "Results": [],
  "NrOfResults": "0",
  "StartIndex": "0",
  "TotalNrOfResults": "0"
}
```

> Note: NrOfResults returns the size of the current page, regardless of the requested size.

### Paged filter parameters {#page-filter}

| Query parameter | Description | Default | Maximum |
| --- | --- | --- | --- |
| nrOfResults | Number of results per page | 25 | 100 |
| startIndex | Index of result where to start | 0 |

## Modules {#modules}

### Listing modules {#listing_modules}

Retrieve a [Page](#page) of [Modules](#module-object) using a `GET` request
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Only modules for this organisationId or having `ActiveForAllOrganisations` |  |
| name | Only return modules with this name (case insensitive). Wildcards \* are allowed. |  |
| pluginName | Only return modules having a plugin with this name (case insensitive). Wildcards \* are allowed . |  |
| pluginId | Only return modules having a plugin with this ID. |

> Note: When `organisationId` is provided, organisation specific plugin configuration is returned. Otherwise, the response contains the default plugin configuration.

#### Response

- `200` A [Page](#page) of [Modules](#module-object)
- `400` The request is not valid
- `403` The user does not have access to the organisation

#### Authorization functions

- Getting modules for other organisations requires either the `ADMIN_VIEW_ALL_ORGANISATIONS` function or the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Getting a module (organisation specific) {#fetching_module}

A single module, including plugin configuration (default or organisation specific) can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules/:id
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Return organisation specific plugin configuration |  |

> Note: If `organisationId` is not provided, the default plugin configuration is returned.

#### Response

- `200` Ok. Body: [Module](#module-object)
- `400` The request is not valid
- `404` The module or organisation does not exist

#### Authorization functions

- Any authenticated user can access this resource
- Getting a module for other organisations requires either the `ADMIN_VIEW_ALL_ORGANISATIONS` function or the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Getting a module (default) {#fetching_module}

A single module, including default plugin configuration can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules/:id/default
```

#### Response

- `200` Ok. Body: [Module](#module-object)
- `400` The request is not valid
- `404` The module does not exist

#### Authorization functions

- Any authenticated user can access this resource

### Updating a module {#updating_module}

A module can be updated by performing a `PUT` request with a [Module](#module-object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules/:id
```

#### Response

- `200` Ok. Body: [Module](#module-object)
- `400` The request is invalid
- `403` The user does not have the required functions
- `404` The module does not exist

#### Authorization functions

- Updating a module always requires the `ADMIN_MODULES` function.
- Updating the property `ActiveForAllOrganisations` also requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Check if a plugin is active for an organisation {#listing_modules}

Check if a plugin is active using a `HEAD` request
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules/active
```

The following query parameters can be used:

| Query parameter | Description | Required | Default |
| --- | --- | --- | --- |
| pluginId | The plugin ID to check whether it is active | Yes |  |
| organisationId | The organisation in question | Yes |  |

Note that plugins from modules that active for all organisations will also count.
The response will contain a header element with the name `Result-Count` with `0` meaning not active and `1` active.
If the plugin does not exist, the result will be not active.

#### Response

- `200` Ok.
- `400` The request is not valid
- `403` User has no access to the organisation
- `404` The organisation does not exist

#### Authorization functions

- Check if a plugin is active for other organisations requires either the `ADMIN_VIEW_ALL_ORGANISATIONS` function or the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Getting the organisations of a module {#module_list_organisations}

To list all organisations linked to a module, do a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules/:id/organisations
```

The standard [Page parameters](#page-filter) are available.

> Note: For modules where `ActiveForAllOrganisations = true`, all organisations are returned.

#### Authorization functions

- Using this endpoint requires at least one of the following
  functions: `ADMIN_VIEW_ALL_ORGANISATIONS`, `ADMIN_EDIT_ALL_ORGANISATIONS`.

#### Response

- `200` A [Page](#page) of [Organisations](#organisation-object)
- `401` User is not authorized
- `403` User does not have the required functions to call this method
- `404` The module does not exist

### Linking organisations with a module {#module_link_organisations}

Link one or more additional organisations with a module using a `PATCH` request containing as body a JSON array of
organisation IDs.
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules/:id/organisations
```

> Note: Linking organisations with modules where `ActiveForAllOrganisations = true` is allowed, but has no added value.

#### Response

- `204` Success
- `400` No organisations are in the list
- `401` User is not authorized
- `403` User does not have the required functions to call this method
- `404` The module or one of the organisations do not exist

#### Authorization functions

- Linking your own organisation requires the `ADMIN_MODULES` function.
- Linking any other organisation requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Unlinking organisations from a module {#module_unlink_organisations}

Unlink organisations from a module using a `DELETE` request containing as body a JSON array of organisation IDs.
```
https://archief.viaa.be/mediahaven-rest-api/v2/modules/:id/organisations
```

#### Response

- `204` Success
- `400` No organisations are in the list
- `403` User is not authorized
- `403` User does not have the required functions to call this method
- `404` The module or one of the organisations do not exist

#### Authorization functions

- Unlinking your own organisation requires the `ADMIN_MODULES` function.
- Unlinking any other organisation requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Getting a plugin (organisation specific) {#fetching_plugin}

The configuration of a module plugin (default or organisation specific) can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/module-plugins/:id
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Return organisation specific plugin configuration |  |

> Note: If `organisationId` is not provided, the default plugin configuration is returned.

#### Response

- `200` Ok. Body: [Plugin](#plugin-object)
- `400` The request is not valid
- `404` The module plugin or organisation does not exist

#### Authorization functions

- Requesting the plugin configuration of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` or `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Getting a plugin (default) {#fetching_plugin_default}

The default configuration of a module plugin can be fetched by performing a `GET` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/module-plugins/:id/default
```

#### Response

- `200` Ok. Body: [Plugin](#plugin-object)
- `400` The request is not valid
- `404` The module plugin does not exist

#### Authorization functions

- Any authenticated user can access this resource

### Partial update of a module plugin (organisation specific) {#updating_plugin_partial}

A module plugin can be partially updated by performing a `PATCH` request with an [UpdatePlugin](#plugin-update-object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/module-plugins/:pluginId
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Update organisation specific plugin configuration. |  |

Notes:
- Providing `organisationId` updates only that organisation’s plugin configuration. Without it, only the general configuration is updated and organisation specific overrides remain unchanged.
- The result of the update returns the full plugin configuration: organisation specific values where available, and otherwise the general values.
- A `PATCH` request only modifies the fields explicitly provided with a non-null value. Fields set to null or omitted from the request body are ignored and remain unchanged.

#### Response

- `200` Ok. Body: [Plugin](#plugin-object)
- `400` The request is invalid
- `403` The user does not have the required functions
- `404` The plugin or organisation does not exist
- `409` The plugin cannot be updated because the plugin is not active for the given organisation

#### Authorization functions

- Updating organisation specific plugin configuration of your own organisation requires the `ADMIN_MODULES` function.
- Updating organisation specific plugin configuration of a different organisation requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` functions.
- Updating general plugin configuration requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` functions.

### Partial update of a module plugin (default) {#updating_plugin_partial_default}

The default configuration of a module plugin can be partially updated by performing a `PATCH` request with an [UpdatePlugin](#plugin-update-object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/module-plugins/:pluginId/default
```

Notes:
- Organisation specific configuration remain unchanged.
- A `PATCH` request only modifies the fields explicitly provided with a non-null value. Fields set to null or omitted from the request body are ignored and remain unchanged.

#### Response

- `200` Ok. Body: [Plugin](#plugin-object)
- `400` The request is invalid
- `403` The user does not have the required functions
- `404` The plugin does not exist
- `409` The plugin cannot be updated because the plugin is not active for the given organisation

#### Authorization functions

- Updating general plugin configuration requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` functions.

### Full update of a module plugin (organisation specific) {#updating_plugin_full}

A module plugin can be fully updated by performing a `PUT` request with an [UpdatePlugin](#plugin-update-object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/module-plugins/:pluginId
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Update organisation specific plugin configuration |  |
| fallbackToDefault | Use default config when a property is null or missing. Only applies when organisationId is provided. | false |

Notes:
- Providing `organisationId` updates only that organisation’s plugin configuration. Without it, only the general configuration is updated and organisation specific overrides remain unchanged.
- The result of the update returns the full plugin configuration: organisation specific values where available, and otherwise the general values.
- A `PUT` request replaces all values: null and missing fields override existing ones. With `fallbackToDefault`, they fall back to the default config when `organisationId` is used.

#### Response

- `200` Ok. Body: [Plugin](#plugin-object)
- `400` The request is invalid
- `403` The user does not have the required functions
- `404` The plugin or organisation does not exist
- `409` The plugin cannot be updated because the plugin is not active for the given organisation

#### Authorization functions

- Updating organisation specific plugin configuration of your own organisation requires the `ADMIN_MODULES` function.
- Updating organisation specific plugin configuration of a different organisation requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` functions.
- Updating general plugin configuration requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` functions.

### Full update of a module plugin (default) {#updating_plugin_full_default}

The default configuration of a module plugin can be fully updated by performing a `PUT` request with an [UpdatePlugin](#plugin-update-object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/module-plugins/:pluginId/default
```

Notes:
- Organisation specific configuration remain unchanged.
- A `PUT` request replaces all values: null and missing fields override existing ones.

#### Response

- `200` Ok. Body: [Plugin](#plugin-object)
- `400` The request is invalid
- `403` The user does not have the required functions
- `404` The plugin does not exist
- `409` The plugin cannot be updated because the plugin is not active for the given organisation

#### Authorization functions

- Updating general plugin configuration requires the `ADMIN_MODULES` and `ADMIN_EDIT_ALL_ORGANISATIONS` functions.

### Module object structure {#module-object}

| Property | Type | Description | readonly |
| --- | --- | --- | --- |
| Id | String | A unique module id. | Yes |
| Name | String | The unique name of the module. | Yes |
| Plugins | [Plugin](#plugin-object)[] | The plugins linked to this module. | Yes |
| ActiveForAllOrganisations | boolean | Whether the module is active for all organisations. | No |

Example:
```
{
  "Id": "FULL-TEXT-SEARCH-POC",
  "Name": "Full-text search (POC)",
  "Plugins": [
    {
      "Id": "OCR",
      "Name": "Optical Character Recognition",
      "Uri": null,
      "DottedKey": null
    },
    {
      "Id": "PERCEPTUAL-HASH",
      "Name": "Perceptual hash",
      "Category": "Embedding",
      "Uri": "https://ai-connector.zeticon.com/ai/connectors/perceptual-hash/",
      "DottedKey": "Technical.Embeddings.PerceptualHash"
    }
  ],
  "ActiveForAllOrganisations": false
}
```

### Plugin object structure {#plugin-object}

| Property | Type | Description |
| --- | --- | --- |
| Category | Enum | The type of plugin: Feature, Embedding |
| Id | String | A unique plugin ID |
| Name | String | Name of the plugin |
| Uri | String | (Optional) The URI of the (external) plugin to contact |
| DottedKey | String | (Optional) The field definition linked with the plugin |
| CustomProperties | Object | (Optional) Additional properties as nested JSON object |

Example:
```
{
  "Id": "EMBEDDING-OPEN-AI",
  "Name": "Embedding by Open AI",
  "Category": "Embedding",
  "Uri": "https://ai-connector.zeticon.com/ai/connectors/open-ai/",
  "DottedKey": "Technical.Embeddings.OpenAi",
  "CustomProperties": {
    "TextModel": "ada2"
  }
}
```

### Plugin update object structure {#plugin-update-object}

Note that the `Secret` can only be updated, never retrieved.

| Property | Type | Description | Overridable per organisation (\*) |
| --- | --- | --- | --- |
| Category | Enum | (Optional) The type of plugin: Feature, Embedding | No |
| Name | String | (Optional) Name of the plugin. Must be unique per organisation | Yes |
| Uri | String | (Optional) The URI of the (external) plugin to contact | Yes |
| Secret | String | (Optional) Secret to provide to the plugin | Yes |
| DottedKey | String | (Optional) The field definition linked with the plugin | Yes |
| CustomProperties | Object | (Optional) Additional properties as nested JSON object | Yes |

(\*) This column indicates which properties can be overridden per organisation using the organisation-specific `PATCH` endpoint.

Example:
```
{
  "Secret": "<Our very secret API key>",
  "DottedKey": "Technical.Embeddings.OpenAi",
  "CustomProperties": {
    "TextModel": "ada3"
  }
}
```

## Schemas {#schemas}

### Description {#schemas_description}

With the following endpoints you can request XSD schemas, either general or classification-specific.

### Get general schema {#schema_general}

Retrieve a general XSD using a `GET` request:
```
https://archief.viaa.be/mediahaven-rest-api/v2/schema
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| schemaVersion | The mediahaven schema version | head |
| type | The type of schema (Mhs, Mh) | Mhs |

#### Response

- `200` An XSD schema
- `400` The request is not valid

### Get classification schema {#schema_classification}

Retrieve an XSD for a specific classification using a `GET` request:
```
https://archief.viaa.be/mediahaven-rest-api/v2/classifications/{id}/schema
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| recordType | The record type for which you want to request the schema |  |
| type | The type of schema (Mhs, Mhd) | Mhs |
| version | The version of the classification. Either the specific number, or versioning status: Draft,Head | 1 |
| schemaVersion | The mediahaven schema version | head |

The following types are supported:

- Mhs: Mediahaven sidecar format, which is the format supported for ingesting
- Mhd: Mediahaven dynamic fields format, which is the dynamic field list for the given classification

#### Response

- `200` An XSD schema
- `400` The request is not valid
- `404` The classification does not exist

### Error result {#error}

#### Error object {#error_object}

| Property | Type | Description |
| --- | --- | --- |
| Message | String | The message the error returns. |
| Status | Number | The HTTP error code. |
| Code | String | the corresponding error code. |

### Example {#mediahaven-rest-api-manual-schemas-example}
```
{
  "Message": "User is not authorized. Please check if authorization headers are correctly set",
  "Status": 401,
  "Code": "EUNAUTH"
}
```

### Duplicate error result {#error_duplicate}

#### Duplicate error object {#error_duplicate_object}

| Property | Type | Description |
| --- | --- | --- |
| Message | String | The message the error returns. |
| Status | Number | The HTTP error code. |
| Code | String | the corresponding error code. |
| ExistingRecordIds | List | List of existing record ids for the given metadata |
| ExistingRecords.[].RecordId | String | The record id of a duplicate record |
| ExistingRecords.[].RecordType | String | The record type of a duplicate record |
| ExistingRecords.[].DataRecordId | String | The record id of the data record, if applicable |
| ExistingRecords.[].Versioning.Id | String | The versioning id of the record, if applicable |
| ExistingRecords.[].Versioning.Version | Number | The version number of the record, if applicable |
| ExistingRecords.[].Versioning.Status | Number | The version status of the record, if applicable |

### Example {#mediahaven-rest-api-manual-schemas-example}
```
{
  "Message": "File already available for your organisation",
  "Status": 409,
  "Code": "EDUPLICATE",
  "ExistingRecordIds": [
    "a18ff9ed2a2f441f9a4fdb0bc6554165800cf4384802479287df140832a877b3"
  ],
  "ExistingRecords": [
    {
      "RecordId": "a18ff9ed2a2f441f9a4fdb0bc6554165800cf4384802479287df140832a877b3",
      "RecordType": "Representation",
      "DataRecordId": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
      "Versioning": {
        "Id": "c7b989e28e1b4300935ac049b5db74580566e5a28f64403e957312bb1f35eab1",
        "Version": 1,
        "Status": "Head"
      }
    }
  ]
}
```

> Note: The returned error description can change without prior notification, you should not rely on its content.

### Error Codes {#error_codes}

General error codes:

| Error Code | HTTP Status code | Description (can be more specific depending on context) |
| --- | --- | --- |
| EUNAUTH | 401 | User is not authorized. Please check if authorization headers are correctly set |
| ENOTFND | 404 | Resource cannot be found |
| EFORBID | 403 | User has unsufficient rights / no access |
| ENORIGHT | 403 | User has insufficient rights |
| ENOACCES | 403 | User has no access |
| EREADONLY | 403 | Field is readonly |
| ENOTALLOWED | 405 | HTTP 405 Method Not Allowed |
| EBADREQ | 400 | Parameters are missing or invalid |
| ETOOMANYREQ | 429 | Too many simultaneous requests, try again later |
| EPARAMREQ | 400 | Required parameter is missing |
| EJSONINV | 400 | Provided data is not valid JSON |
| EPARAMINV | 400 | Required parameter is invalid |
| EDUPLICATE | 409 | File is already present |
| ENTYETAVAIL | 409 | File is being processed |
| ESERVER | 500 | Internal server error, issue should be reported to <https://mediahaven.freshdesk.com> or support@zeticon.com |
| ECLIENT | 400 | Any other client error, check the status code and follow the HTTP spec |
| ENOTIMPL | 501 | This functionality is not (yet) exposed |
| EINVALIDSTATE | 409 | The environment is in an invalid state |
| ECONFL | 409 | Conflict with the current state of the resource |
| ECONCURRENT | 409 | Concurrent update detected |
| EGONE | 41O | Object is expired |

Specific error codes:

| Error Code | HTTP Status code | Description (can be more specific depending on context) |
| --- | --- | --- |
| FIELD-DEFINITIONS-PROCESSING | 409 | Field definitions are already processing |
| FIELD-DEFINITIONS-MULTIPLE-ACTORS | 409 | Another initiator has already made changes to a field definition or its siblings/parent |
| FIELD-DEFINITIONS-SUBACTION-NOT-ALLOWED | 409 | Subaction is not in the list of allowed field definition actions |
| STORAGE-POOL-NOT-FOUND | 404 | Storage pool does not exist |
| INVALID-SPEL-EXPRESSION | 400 | Invalid SpEL expression |
| INVALID-SERVER-URL | 400 | The url derived from the server properties is not valid |
| INVALID-URL | 400 | Invalid url |

## Release notes {#release_notes}

### 21.2 {#mediahaven-rest-api-manual-release-notes-212}

- [Autocompleting](#autocomplete) generic simple metadata fields
- [Searching](#search_on_location) on location
- [Linking](#role_add_users) a role with a user
- Extra query parameter `publicOnly` when [searching](#basic-searching) for records
- [Restarting](#record-jobs-restart) failed jobs for a record
- Improved documentation by provided a table for all request parameters and bodies, plus an example

### 21.1 {#mediahaven-rest-api-manual-release-notes-211}

Official release of REST 2.0 API

## Timed jobs {#timedjobs}

### Creating a timed job {#timed_job_create}

Timed jobs can be created by performing a `POST` request with [Timed job](#create_timed_job_object) as body to:
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/timed-jobs
```

#### Response

- `201` The created [Timed job](#timed_job_object)
- `400` The request is not valid
- `403` User does not have the correct function or has no access to this endpoint

#### Authorization functions

- The user requires the `ADMIN_BACKEND_SERVICES` function to access this endpoint.

### Getting a specific timed job {#timed_job_get_single}

Retrieve a single [Timed job](#timed_job_object) using a `GET` request
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/timed-jobs/:timedJobId
```

#### Response

- `200` Single [Timed job](#timed_job_object)
- `403` User does not have the correct function or has no access to this endpoint
- `404` Timed job was not found

#### Authorization functions

- The user requires the `VIEW_BACKEND_MONITORING` function to access this endpoint.

### Getting all timed jobs {#timed_jobs_get_all}

Retrieve a [Page](#page) of [Timed job](#timed_job_object) using a `GET` request:
```
https://archief.viaa.be/mediahaven-rest-api/v2/timed-jobs
```

The standard [Page parameters](#page-filter) are available.

#### Response

- `200` A [Page](#page) of [Timed job](#timed_job_object)
- `403` User does not have the correct function or has no access to this endpoint

#### Authorization functions

- The user requires the `VIEW_BACKEND_MONITORING` function to access this endpoint.

### Update timed job {#update_timed_job}

Timed jobs can be updated by performing a `PUT` request with [Timed job](#timed_job_object) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/timed-jobs/:timedJobId
```

#### Response

- `204` The timed job was updated
- `403` User does not have the correct function or has no access to this endpoint
- `404` The timed job does not exist

#### Authorization functions

- The user requires the `ADMIN_BACKEND_SERVICES` function to access this endpoint.

### Delete timed job {#timed_job_delete}

Delete a timed job using a `DELETE` request:
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/timed-jobs/:timedJobId
```

#### Response

- `204` The timed job was deleted
- `403` User does not have the correct function or has no access to this endpoint
- `404` Timed job was not found

#### Authorization functions

- The user requires the `ADMIN_BACKEND_SERVICES` function to access this endpoint.

### Create timed job object structure {#create_timed_job_object}

| Property | Description | Type | Default Value | Required |
| --- | --- | --- | --- | --- |
| Name | The name of the timed job | String |  | yes |
| ProcessDefinition | The name of the process | String |  | yes |
| ProcessVariables | The process variables of the timed job | Map |  | no |
| Delay | The time between each timed job (in minutes) | Integer | 5 | no |
| Enabled | If true, allows for disabling/pausing a timed job | Boolean | false | no |
| UserPriority | If defined, start the workflow with this priority. Allowed values are: HIGH, NORMAL, LOW, BACKGROUND. | UserPriority |  | no |
```
{
  "Name": "Exports cleanup",
  "ProcessDefinition": "exports_cleanup",
  "ProcessVariables": {
    "var1": "value"
  },
  "Delay": 5,
  "Enabled": true,
  "UserPriority": "HIGH"
}
```

### Timed job object structure {#timed_job_object}

| Property | Description | Type | Default Value | Required |
| --- | --- | --- | --- | --- |
| Id | A unique timed job id | String (UUID) |  | yes |
| Name | The name of the timed job | String |  | yes |
| ProcessDefinition | The name of the process | String |  | yes |
| ProcessVariables | The process variables of the timed job | Map |  | no |
| UserPriority | If defined, start the workflow with this priority. Allowed values are: HIGH, NORMAL, LOW, BACKGROUND. | UserPriority |  | no |
| Delay | The time between each timed job (in minutes) | Integer | 5 | no |
| LastExecution | The last time the job was executed | Date (ISO8601) |  | no |
| NextExecution | The next time the job will be executed (the start time of the previous tick plus the delay) | Date (ISO8601) |  | no |
| Enabled | If true, allows for disabling/pausing a timed job | Boolean | false | no |
| LastFailure | The last time the job failed | Date (ISO8601) |  | no |

Example:
```
{
  "Id": "9430ddb5-cedb-4fff-b1ba-f61f96828162",
  "Name": "Exports cleanup",
  "ProcessDefinition": "exports_cleanup",
  "ProcessVariables": {
    "Var1": "value"
  },
  "Delay": 5,
  "LastExecution": "2021-03-23T09:39:12.101000Z",
  "NextExecution": "2021-03-23T09:44:12.101000Z",
  "Enabled": true,
  "LastFailure": null

}
```

## Domains {#domains}

Domains represent all the urls that can be used to access the application.

### Public domain info {#get_public_domaininfo}

A special endpoint `/tenant-information` has been provided to access the domain information of a particular url without
having to be logged in.
you can get this info by doing a `GET` call to the following URL:
```
https://archief.viaa.be/tenant-info
```

#### Response

- `200` The [Domain](#domain_object)
- `404` The domain for the current url could not be found

#### Authentication

This endpoint does not require any authentication.

### Listing all domains {#get_all_domains}

A list of all domains can be retrieved using a `GET` call to the following endpoint:
```
https://archief.viaa.be/mediahaven-rest-api/v2/domains
```

The standard [Page parameters](#page-filter) are available.

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | Organisation to search for | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |

> Note: A user without the ADMIN_VIEW_ALL_ORGANISATIONS function can only see domains of their own organisation

#### Response

- `200` A [Page](#page) of [Domains](#domain_object)
- `400` The request is not valid

#### Authorization functions

- Requesting domains of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Getting a domain {#fetching_domain}

A single domain can be fetched by performing a `GET` request to one of the following endpoints:
```
https://archief.viaa.be/mediahaven-rest-api/v2/domains/:id

https://archief.viaa.be/mediahaven-rest-api/v2/domains/:uri
```

#### Response

- `200` Ok. Body: [Domain](#domain_object)
- `403` User has no access to the domain
- `404` The domain does not exist

#### Authorization functions

- Requesting domains of a different organisation requires the `ADMIN_VIEW_ALL_ORGANISATIONS` function.

### Creating a domain {#create_domain}

A domain can be created by performing a `POST` request with [Domain](#domain_object) as body to one of the following endpoints:
```
https://archief.viaa.be/mediahaven-rest-api/v2/domains
```

#### Response

- `200` Ok. Body: [Domain](#domain_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the organisation in question.

#### Authorization functions

- Creating domains requires the `ADMIN_DOMAINS` function.
- Creating a domain for a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Update a domain {#update_domain}

Updating a domain can be done by performing a PUT-request with [Domain](#domain_object) as body to one of the following endpoints:
```
https://archief.viaa.be/mediahaven-rest-api/v2/domains/:id

https://archief.viaa.be/mediahaven-rest-api/v2/domains/:uri
```

#### Response

- `200` Ok. Body: Updated [Domain](#domain_object)
- `400` One or more of the provided property values were not valid.
- `403` No access to the domain in question.
- `404` The domain could not be found

#### Authorization functions

- Updating domains requires the `ADMIN_DOMAIN` function.
- Updating a domain for a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Delete a domain {#delete_domain}

A domain can be deleted by performing a `DELETE` request to one of the following endpoints:
```
https://archief.viaa.be/mediahaven-rest-api/v2/domains/:id

https://archief.viaa.be/mediahaven-rest-api/v2/domains/:uri
```

#### Response

- `204` The domain was deleted.
- `403` No access to the domain in question.
- `404` The domain does not exist.

#### Authorization functions

- The `ADMIN_DOMAINS` function is required to delete a domain
- Deleting a domain of a different organisation requires the `ADMIN_EDIT_ALL_ORGANISATIONS` function.

### Domain object structure {#domain_object}

| Property | Type | Description | Read-only | Required | Default |
| --- | --- | --- | --- | --- | --- |
| Id | String | The id of this domain | Yes |  |  |
| Uri | String | The uri of this domain. Must be unique across all organisations. | No | Yes |  |
| OrganisationId | String | The id of the organisation this domain belongs to. | No | Yes |  |
| OrganisationName | String | The name of the organisation this domain belongs to. | Yes |  |  |
| Shared | Boolean | If True, the domain can be used by users from different organisations. Can only be true for the primary organisation. | No | Yes |  |
| PubliclyAccessible | Boolean | If true, the domain will be linked to an api key for the public user of its organisation. | No | No | False |
| ApiKeys | Array | List of [api keys](#api_key_object) that are available for this domain. | Yes |  | [] |
```
{
  "Id": "73db6850-02bb-40bd-9722-ca6fb64115b4",
  "Uri": "mh-dev.mediahaven.com",
  "OrganisationId": "100",
  "OrganisationName": "mh-dev",
  "Shared": false,
  "PubliclyAccessible": true,
  "ApiKeys": [
    {
      "Name": "mh-dev_portal",
      "Value": "MyGeneratedKey"
    }
  ]
}
```

### Api key structure {#api_key_object}

| Property | Type | Description |
| --- | --- | --- |
| Name | String | The name of the api key. |
| Value | String | The actual api key. Value will be regenerated on each update. |
```
{
  "Name": "mh-dev_portal",
  "Value": "MyGeneratedKey"
}
```

## Caches {#caches}

This endpoint is used to manage the caches. Refreshing caches are needed when changes were made by legacy
scripts without using the API.

### Refresh a cache {#caches_refresh_all}

The caches can be refreshed by making a `POST` request without body to
```
https://archief.viaa.be/mediahaven-rest-api/v2/caches/:cache/refresh
```

Available caches to refresh are

| Cache name | Effect |
| --- | --- |
| all | Refreshes all caches |
| field-definitions | Refreshes the field definition cache plus refreshes the field definitions in SOLR |

#### Response

- `202` The cache(s) from this service were refreshed locally, caches from other services will be cleared asynchronously
- `400` Invalid cache name
- `403` User does not have the function `ADMIN_BACKEND_SERVICES`

#### Authorization functions

- Refreshing the caches requires the `ADMIN_BACKEND_SERVICES` function.

## Ftp-users {#ftp-users}

This endpoint can be manage FTP-users.

### Authorization functions {#mediahaven-rest-api-manual-ftp-users-authorization-functions}

This endpoint requires the `ADMIN_BACKEND_SERVICES` function.

### Creating an FTP user {#create_ftp_user}

Creating an FTP-USER can be done by performing a `POST` request with a [FTP-user](#ftp_user_data_model) as body to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/ftp-users
```

`Note`: This endpoint is idem-potent. If a user with that username already exists, it will be updated.

#### Response

- `201` Created: [FtpUSer](#ftp_user_data_model)

### Deleting an FTP user {#delete_ftp_user}

Creating a FTP-user can be done by performing a `DELETE` to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/ftp-users/:username
```

#### Response

- `204` No content
- `404` FTP-user not found

### FTP-user object structure {#ftp_user_data_model}

| Status | Meaning | read-only |
| --- | --- | --- |
| Id | The id of the ftp user | Yes |
| Username | The login name | No |
| Password | The password of the ftp user. `Note:` will not be returned in a response body. | No |
| Path | The absolute root directory of the user. Must be a subpath of `/mnt/STORAGE` | No |
| Uid | The uid of the user. Will be determined automatically if not provided. | No |
```
{
  "Username": "storage@mh-dev",
  "Password": "*****",
  "Path": "/mnt/STORAGE/example",
  "Uid": 30
}
```

## Actions {#actions}

### Get a list of all possible actions {#list_actions}

In order to get a list of all possible actions, do a `GET`-request to the following endpoint:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/actions
```

#### Response

- `200` List of [Actions](#action-object)

### Execute an action {#actions_execute}

In order to execute a specific action, do a `POST`-request to the following endpoint:
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/actions/:actionName
```

The records on which the action is executed is either specified by a list of record IDs or a search request. Based on
internal logic, the action on the records will be done synchronously in this request or an asynchronous batch is created
to
perform the action on the records. If no batch ID is returned, the execution is already synchronously completed. If a
batch is
returned check the status of the [Batch](#batches_get_single) for its asynchronous completion.

#### Response

- `200` [Execute action response](#action-execute-response)
- `400` One of the request properties contains an invalid value.
- `404` One or more provided `RecordIds` were not found

### Action execute object {#action-execute-object}

| Property | Type | Description | Required |
| --- | --- | --- | --- |
| RecordIds | Array | List of record IDs on which on the action will be executed. Mutually exclusive with the property `SearchRequest`. | yes\* |
| SearchRequest.Query | String | The Solr query specifying the record on which the action will be executed. Mutually exclusive with the property `RecordIds`. | yes\* |
| Arguments | Object | Optional arguments to execute the specific action | no |
```
{
  "RecordIds": [
    "<Record ID A>",
    "<Record ID B>",
    "<Record ID C>"
  ],
  "Arguments": {
    "Comment": "The submission of the objects have been declined because their description is too short"
  }
}
```

```
{
  "SearchRequest": {
    "Query": "+Administrative.RecordType:Mh2Collection +Administrative.RecordStatus:Published +Administrative.PublicationDate:[* TO 2020-01-01T00:00:00.000000Z]"
  },
  "Arguments": {
    "Reason": "Decision to archive our oldest collections by the steering committee."
  }
}
```

### Action execute response {#action-execute-response}

| Property | Type | Description |
| --- | --- | --- |
| BatchId | String | ID of the batch that has been optionally created |
| Executions | Array | List of [execution results](#action-execute-response-execution) when no batch was created |

#### Action execute response: single execution result {#action-execute-response-execution}

| Property | Type | Description |
| --- | --- | --- |
| RecordId | String | ID of the record |
| Status | String | Whether the execution was `Completed` or `Failed` |
| ErrorMessage | String | Message when it failed |

#### Example
```
{
  "BatchId": "<Batch ID>",
  "Executions": []
}
```

```
{
  "BatchId": null,
  "Executions": [
    {
      "RecordId": "Record ID A",
      "Status": "Completed",
      "ErrorMessage": null
    },
    {
      "RecordId": "Record ID B",
      "Status": "Failed",
      "ErrorMessage": "User test does not have publish rights"
    },
    {
      "RecordId": "Record ID C",
      "Status": "Completed",
      "ErrorMessage": null
    }
  ]
}
```

### Action object {#action-object}

| Property | Type | Description |
| --- | --- | --- |
| Name | String | The name of the action. |
| Label | String | The label of the action that matches with the current user locale. |
| Labels | Array | Contains all the available labels per language. |
| Description | String | The description of the action that matches with the current user locale. |
| Descriptions | Array | Contains all the available descriptions per language. |
| Function | String | The function required to execute this action. |
| RequiredPermissions | Array | The permissions required to execute the actions. Possible values:  *Read*  Write \* Export. |
| Href | String | The url part that will be used for the action. |
| HttpMethod | String | The http method used for the action. |
| ContentType | String | The expected content type for the body. |
| EventType | String | The subtype of the premis event generated when the action is executed. |

Notes:
- `Labels` and `Descriptions` contains translations for each supported locale. If no translation is defined for a specific locale, a fallback will be used, namely the first non-empty value from the following list:
- The translation for the default locale with the same language (for example if `nl_NL` is not defined, `nl_BE` can be used)
- The translation for the ‘overall’ default locale `en_US`
- Empty value
```
{
  "Name": "publish",
  "Label": "Publish",
  "Labels": [
    {
      "Lang": "en",
      "Value": "Publish"
    },
    {
      "Lang": "nl",
      "Value": "Publiceer"
    }
  ],
  "Description": "Publish a record",
  "Descriptions": [
    {
      "Lang": "en",
      "Value": "Publish a record"
    },
    {
      "Lang": "nl",
      "Value": "Publiceer een object"
    }
  ],
  "Function": "PUBLISH_MEDIA",
  "RequiredPermissions": ["Read", "Write"],
  "Href": "publish",
  "HttpMethod": "POST",
  "ContentType": "application/json",
  "EventType": "PUBLISH"
}
```

## Record actions {#record-actions}

The api provides a list of actions that are possible on records.
By default, the possible actions are not returned. You can request them by setting the accept header
to `application/hal+json`
When the accept header is set the response of the `/record` or `/records` endpoint will contain a `_links` element.

The action itself has a rel attribute which refers to the action-model.

Example:
```
{
  "Internal": {
    "RecordId": "0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758",
    "HasKeyframes": false,
    "IngestSpaceId": null,
    "IsFragment": false
  },
  "_links":  [
      {
        "Rel": "delete",
        "Href": "https://archief.viaa.be/mediahaven-rest-api/v2/records/0763d8751eda4dd09f4b2fcd5f637489c41f475410524a02923e5290c5788758/actions/delete",
        "Method": "DELETE",
        "State": "Allowed",
        "Type": "application/json"
      },
      {
        "Rel": "publish",
        "State": "Disallowed",
        "Reasons": [
          {
            "Code": "RecordStatusNotPublishable",
            "Value": "Record can not be published in its current status"
          }
        ]
      }
    ]
}
```

### Record Action object {#record-action-object}

| Property | Type | Description | Possible values | Required |
| --- | --- | --- | --- | --- |
| Rel | String | Referrer to a action definition |  | yes |
| Href | String | Absolute url to the action |  | yes |
| Method | String | Request method | GET, POST, DELETE, PUT, PATCH | yes |
| State | String | Is the action allowed for the current user. In a list you can get the value ‘Deferred’. To get the actual state you will have to fetch the single record. | Allowed, Disallowed, Deferred | yes |
| Reasons[] > Code | String | A code to represent the reason why this actions is not allowed on the record |  | no |
| Reasons[] > Value | String | A description you can represent to the user why the action is not available |  | no |
| Type | String | Expected Content-Type of the request |

## Record storage {#record_storage}

The api endpoint provides storage info about a record.

### Required functions {#mediahaven-rest-api-manual-record-storage-required-functions}

- `VIEW_BACKEND_MONITORING`: View storage info
- `ADMIN_BACKEND_SERVICES`: Allocate, update or delete storage

### Getting storage linked to a record {#record_storage_list}
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/storage
```

| Query parameter | Type | Description | Default | Required |
| --- | --- | --- | --- | --- |
| cluster | String | cluster of storage pool |  | no |
| clusterGroup | String | cluster group of storage pool |  | no |
| type | String | type of storage pool |  | no |
| role | String | role of storage pool |  | no |
| includeDeleted | Boolean | include logically or permanent deleted storage pools | `false` | no |

Responds with a list of [[record storage object](#record-storage-object)].

Example:
```
[
  {
    "StoragePoolId": 0,
    "Protocol": "file",
    "Cluster": "ingest",
    "ClusterGroup": "ingest",
    "DistributionId": null,
    "StorageType": "DISK",
    "DeleteStatus": "NotDeleted",
    "Role": "TRANSIENT",
    "Rank": 1,
    "Online": true,
    "ActualRecordId": "2ae64fa5dc6147239f8956ed4049eb7cfd55a00695f24136b2ee826a99c3419a",
    "ActualSubPath": null,
    "ResolvedRecordId": "2ae64fa5dc6147239f8956ed4049eb7cfd55a00695f24136b2ee826a99c3419a"
  }
]
```

### Getting a specific pool linked to a record {#record_storage_specific}
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/storage/:storagePoolId
```

Responds with [record storage object](#record-storage-object)

### Update a specific pool linked to a record {#record_storage_update}
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/storage/:storagePoolId
```

Send a request with [record storage object](#record-storage-object) as body.

The only option is to change the distributionId, existing distributionId can’t be updated.

### Delete a specific pool linked to a record {#record_storage_delete}

Unlinks a specific storage pool from a record. This operation is restricted to users with `ADMIN_BACKEND_SERVICES` permission.
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/records/:recordId/storage/:storagePoolId
```

**Request Body (Optional)**

| Property | Type | Description | Required |
| --- | --- | --- | --- |
| EventType | String | The type of event to be recorded | No |
```
{
  "EventType": "ARCHIVE.REMOVED"
}
```

#### Response

- `204` No content
- `401` Unauthorized
- `403` Forbidden
- `404` The record or storage pool was not found

### Record Storage object {#record-storage-object}

| Property | Type | Description | Possible values | Readonly | Required |
| --- | --- | --- | --- | --- | --- |
| StoragePoolId | Number | The id of the storage pool |  | yes | yes |
| Protocol | String | Protocol of the storage pool |  | yes | yes |
| Cluster | String | Cluster of the storage pool |  | yes | yes |
| ClusterGroup | String | Cluster group of the storage pool |  | yes | yes |
| DistributionId | String | Unique distribution id used by this storage |  | no | no |
| StorageType | String | Type of storage pool | DISK,TAPE | yes | yes |
| DeleteStatus | String | Is the file still present on this storage | NotDeleted, LogicallyDeleted, PermanentlyDeleted | yes | yes |
| Role | String | Role of the storage | ARCHIVE, BACKUP, VAULT, TRANSIENT, EXTERNAL, DISTRIBUTION, EXPORT | yes | yes |
| Rank | Number | Rank, used during export to determine source |  | yes | yes |
| Online | Boolean | Whether the storage is currently online/reachable |  | yes | yes |
| ActualRecordId | String | Record id for which the file is saved under on storage if it differs from the id of the record itself. |  | yes | no |
| ActualSubPath | String | Sub Path for which the file is saved under on storage |  | yes | no |
| ResolvedRecordId | String | The record id used on the storage. Equal to `ActualRecordId` if provided, else equal to the ‘RecordId’ of the record. |  | yes | yes |

## Version {#version}

Returns the current version of the API.

### Required functions {#mediahaven-rest-api-manual-version-required-functions}

No functions are required to call this endpoint.

### Get the version {#version-get}

To obtain the version make a `GET` request
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/version
```

#### Response

- `200` OK [Version](#version_model)

## Roles object structure {#roles_datamodel}

| Property | Type | Description |
| --- | --- | --- |
| Version | String | String version |
| VersionNumber | Number | A number representation of the version (ex 24.1) |
| BuildVersion | String | The full version number (with minor) |

## Shares {#shares}

Shares allow records to be shared with internal or external recipients, enabling them to view, download previews, and, if permitted, modify metadata or access original files.
A [share token](#obtain_share_token) can be used to access a share’s objects via the API with the correct permissions, without needing extra parameters.

### Getting a specific share {#get_single_share}

A single [Share](#share_object) can be fetched by performing a `GET`-request to:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/shares/:shareId
```

#### Response

- `200` Single [Share](#share_object).
- `401` User is not authorized.
- `404` The share could not be found.

#### Authorization functions

- Any authenticated user can access this resource.

### Creating a share {#create_share}

A share can be created by performing a `POST`-request with [Share](#share_create_object) as body to:
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/shares
```

If the `Records` field contains more than 1 value a [generic selection](#generic-selections) will be created in the
background.

#### Response

- `201` The created [Share](#share_object).
- `400` One or more of the provided property values were not valid.
- `401` User is not authorized.
- `403` User does not have the correct function or has no access to the share object.

#### Authorization functions

- Creating a share requires the function `MANAGE_SHARES`.
- The user must have read rights on the share object.
- Export rights on the share object are also required if the share is marked as `Exportable` = true.

### Deleting a share {#delete_share}

A share can be deleted by performing a `DELETE` request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/shares/:shareId
```

#### Response

- `204` The share was deleted.
- `401` User is not authorized.
- `403` User does not have the correct function.
- `404` The share could not be found.

#### Authorization functions

- Deleting a share requires the function `MANAGE_SHARES`.

### Updating a share {#update_share}

A share can be updated by performing a `POST` request with [Share](#share_object) as body to to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/shares/:shareId
```

#### Response

- `200` The share was update.
- `401` User is not authorized.
- `403` User does not have the correct function.
- `404` The share could not be found.

#### Authorization functions

- Updating a share requires the function `MANAGE_SHARES` and ownership of the share.

### Obtaining a share token {#obtain_share_token}

A share token can be obtained by exchanging a share ID for a token with a `POST`-request to:
```
https://archief.viaa.be/mediahaven-rest-api/v2/shares/:shareId/token
```

For further details on how to use the share token in a request, see [the Confluence documentation.](https://mediahaven.atlassian.net/wiki/spaces/CS/pages/5163155480/Share+tokens#Using-the-share-token)

#### Response

- `200` Ok. Body: A [Share token](#share_token_object).
- `401` User is not authorized.
- `403` The share has expired.
- `404` The share could not be found.

#### Authorization functions

- Any authenticated user can access this resource.

### Create share object structure {#share_create_object}

| Property | Type | Description | Default value | Required |
| --- | --- | --- | --- | --- |
| ExpiryDate | Date (ISO8601) | Optional date after which the share is no longer accessible. If set, it must be later than the share’s creation date. |  |  |
| RequiresLogin | Boolean | Whether the share will be displayed in the public portal or MediaHaven, with the public portal requiring no login. | true |  |
| Exportable | Boolean | Whether the share can be exported. | false |  |
| Records | String[] | List of records to add to the share |  | yes |

Notes:

- `Records` can contain either a `FragmentId`, `MediaObjectId`, or `RecordId`. If a `MediaObjectId` or `RecordId` is
  provided, it will be resolved to the main fragment ID.
- A maximum of 500 items can be added to `Records`
  -
- If a selection is provided in `Records` it’s not allowed to add additional values

### Share object structure {#share_object}

| Property | Type | Description | Readonly |
| --- | --- | --- | --- |
| Id | String (UUID) | A unique share ID. | yes |
| UserId | String (UUID) | User ID who created the share, null when user is removed. | yes |
| CreationDate | Date (ISO8601) | When the share was created. | yes |
| ExpiryDate | Date (ISO8601) | Optional date after which the share is no longer accessible. If set, it must be later than the share’s creation date. |  |
| RequiresLogin | Boolean | Whether the share will be displayed in the public portal or MediaHaven, with the public portal requiring no login. |  |
| Exportable | Boolean | Whether the share can be exported. |  |
| FragmentId | String | The fragment ID of the linked object. | yes |
| ShareLink | String | The full URI to access the share. | yes |
```
{
  "Id": "412f4cab-d23e-4c8c-913b-e215f6584918",
  "UserId": "866050f2-1480-4403-8fec-c10efd38e164",
  "CreationDate": "2025-09-25T09:38:34.188000Z",
  "ExpiryDate": "2011-10-01T00:00:00.000000Z",
  "RequiresLogin": false,
  "Exportable": false,
  "FragmentId": "825cb5efe6b54029a6bd11444be1ed94bc3b2b753dcb6a64ea6baa6711264a8472ebea844873f228c3b",
  "ShareLink": "https://integration.mediahaven.com/shares/412f4cab-d23e-4c8c-913b-e215f6584918/view"
}
```

### Share token object structure {#share_token_object}

| Property | Type | Description |
| --- | --- | --- |
| ShareToken | String | The JWT token representing the share, used in the `Authorization` header for API requests. |
```
{
  "ShareToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLWlk..." // gitleaks:allow
}
```

## Ingest configuration {#ingest_configuration}

Ingest configurations allow control over how objects are processed during ingest.
An ingest configuration defines storage selection rules, transformations to apply, and job priority settings.

Ingest configurations can be scoped to a specific organization or applied installation-wide.
When [uploading files](#uploading), users can specify which ingest configuration to use.
If none is specified, the system automatically selects the default ingest configuration for the organization.

### Getting all ingest configurations {#ingest_configuration_search}

A list of [Ingest Configuration](#ingest_configuration_object) objects can be fetched by performing a `GET`-request to:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/ingest-configurations
```

Additionally, the following query parameters can be used:

| Query parameter | Description | Default |
| --- | --- | --- |
| organisationId | The organisation the filter is part of | If user has the function `ADMIN_VIEW_ALL_ORGANISATIONS`: null, otherwise the organisation of the user |
| default | Whether to filter for default ingest configurations | empty (both default and non-default) |
| excludeSystemWide | Whether to exclude system-wide ingest configurations | false |
| forceSystemWide | Whether to only return system-wide ingest configurations | false |

#### Response

- `200` [Page](#page) of [Ingest Configuration](#ingest_configuration_object) objects.
- `401` User is not authorized.

#### Authorization functions

- Any authenticated user can access ingest configurations from their organization.
- Viewing ingest configurations from other organizations requires the function `ADMIN_VIEW_ALL_ORGANISATIONS`.

### Getting a specific selection configuration {#get_single_selection_configuration}

A single [Ingest Configuration](#ingest_configuration_object) can be fetched by performing a `GET`-request to:
```
GET https://archief.viaa.be/mediahaven-rest-api/v2/ingest-configurations/:id
```

#### Response

- `200` Single [Ingest Configuration](#ingest_configuration_object).
- `401` User is not authorized.
- `403` User does not have the correct function.
- `404` The ingest configuration could not be found.

#### Authorization functions

- Any authenticated user can access ingest configurations from their organization.
- Viewing ingest configurations from other organizations requires the function `ADMIN_VIEW_ALL_ORGANISATIONS`.

### Creating a new ingest configuration {#create_ingest_configuration}

A new [Ingest Configuration](#ingest_configuration_object) can be created by performing a `POST`-request with [Ingest Configuration](#ingest_configuration_object) as body to:
```
POST https://archief.viaa.be/mediahaven-rest-api/v2/ingest-configurations
```

#### Response

- `201` The ingest configuration was created. The body contains the [Ingest Configuration](#ingest_configuration_object) object.
- `400` The request was malformed.
- `401` User is not authorized.
- `403` User does not have the correct function.

#### Authorization functions

- Creating a new ingest configuration requires the function `MANAGE_INGEST_CONFIGURATIONS`.
- Creating a new ingest configuration for a different organisation requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Deleting an ingest configuration {#delete_ingest_configuration}

An ingest configuration can be deleted by performing a `DELETE`-request to:
```
DELETE https://archief.viaa.be/mediahaven-rest-api/v2/ingest-configurations/:id
```

#### Response

- `204` The ingest configuration was deleted.
- `401` User is not authorized.
- `403` User does not have the correct function.
- `404` The ingest configuration could not be found.

#### Authorization functions

- Deleting an ingest configuration requires the function `MANAGE_INGEST_CONFIGURATIONS`.
- Deleting an ingest configuration for a different organisation requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Updating an ingest configuration {#update_ingest_configuration}

An existing [Ingest Configuration](#ingest_configuration_object) can be updated by performing a `PUT`-request with [Ingest Configuration](#ingest_configuration_object) as body to:
```
PUT https://archief.viaa.be/mediahaven-rest-api/v2/ingest-configurations/:id
```

#### Response

- `200` The ingest configuration was updated. The body contains the [Ingest Configuration](#ingest_configuration_object) object.
- `400` The request was malformed.
- `401` User is not authorized.
- `403` User does not have the correct function.
- `404` The ingest configuration could not be found.

#### Authorization functions

- Updating an ingest configuration requires the function `MANAGE_INGEST_CONFIGURATIONS`.
- Updating an ingest configuration for a different organisation requires the function `ADMIN_EDIT_ALL_ORGANISATIONS`.

### Ingest configuration object structure {#ingest_configuration_object}

| Property | Type | Description | Readonly | Default value |
| --- | --- | --- | --- | --- |
| Id | String (UUID) | A unique ID. | yes |  |
| OrganisationId | String | The ID of the [organisation](#organisations) the ingest configuration belongs to. If not set, the ingest configuration is usable for all organizations. | no |  |
| Name | String | The name of the ingest configuration. | no |  |
| Default | Boolean | Whether the ingest configuration is the default for the organisation. | no | false |
| StorageSelection | Enum (Disk,Tape) | The storage selection strategy to use for the share. | no |  |
| Transformations.Ids | List of String (UUID) | List of transformations linked to this ingest configuration. | no |  |
| Transformations.Strategy | Enum (Extend,Force) | `Extend`: If a linked transformation’s parent is selected during ingest, the linked transformation is used. Linked transformations without parent are skipped. `Force`: Only use the linked transformations. The default logic for selecting transformations based on file format is skipped entirely. | no | Extend |
| UserPriority | String | The priority of the ingest. | no | Normal |
```
{
  "Id": "412f4cab-d23e-4c8c-913b-e215f6584918",
  "OrganisationId": "100",
  "Name": "Default ingest",
  "Default": true,
  "StorageSelection": "Disk",
  "Transformations": {
    "Ids": ["512f4cab-d23e-4c8c-913b-e215f6584918", "612f4cab-d23e-4c8c-913b-e215f6584918"],
    "Strategy": "Extend"
  },
  "UserPriority": "Normal"
}
```

## Appendix {#appendix}

### Response status {#status}

If something goes wrong in the server or some input parameters are not compliant with the interface of the webservice, the webservice will reply with an HTTP error code.
For a list of all possible response statuses see: [Response.Status.html](http://docs.oracle.com/javaee/7/api/javax/ws/rs/core/Response.Status.html)

### Special characters in cURL {#special_characters}

When using plain HTTP(S) requests, special characters after the `?q=` have to be URL encoded with percent-encoding,  
Java or a rest client library will do this automatically.

| Code | Symbol |
| --- | --- |
| %20 | space |
| %21 | ! |
| %22 | “ |
| %23 | # |
| %26 | & |
| %27 | ‘ |
| %28 | ( |
| %29 | ) |
| %2A | \* |
| %2B | + |
| %2C | , |
| %2F | / |
| %3A | : |
| %3D | = |
| %3F | ? |
| %40 | @ |
| %5B | [ |
| %5D | ] |

For the full list see: [htmlcodes.html](http://www.ascii.cl/htmlcodes.htm)

### The mediatypes of a record {#mediatypes}

- image
- layer
- video
- videofragment
- audio
- audiofragment
- metadataonly
- document
- page
- newspaper
- newspaperpage
- article
- collection
- set
- processing

### Object statuses {#object_statuses}

MediaHaven has different fields to convey the status of the objects

#### OriginalStatus {#original_status}

Once the OriginalStatus reaches `completed` it will forever hold that status.

| OriginalStatus | Description |
| --- | --- |
| in_progress | The transcoding of the file has not yet begun or is not yet completed |
| failed | Original has not been placed on storage |
| completed | The original file is successfully stored on the MediaHaven system |

#### BrowseStatus {#browse_status}

| BrowseStatus | Description |
| --- | --- |
| in_progress | Creation of the browse is in progress. |
| completed | The browse is successfully created, this does not guarantee that the original is correctly stored |
| failed | The creation of the browse failed |
| cancelled | The browse was not created because a previous step with the original failed, guarantees OriginalStatus != completed |
| no_browse | No browse is created for this file type (e.g. xml or pac) |

#### ArchiveStatus {#archive_status}

Once the ArchiveStatus reaches `on_disk` or `on_tape` it will forever hold that status.

| ArchiveStatus | Description |
| --- | --- |
| on_ingest_tape | The item has been detected by the tape ingest server but has not yet been transferred to the ingest server. |
| in_progress | The item has been detected on the ingest server and is being processed. |
| failed | The item is not successfully processed. |
| on_disk | The item is successfully archived on two or more disks. For files where the ultimate location is tape, this status will not appear. |
| on_tape | The item is successfully archived on N tapes. Depending on the installation N can be 1 (archive), 2 (backup) or 3 (vault). |
| completed | Only used for files of type Metadataonly (`completed` by default) and Ensembles (Collection, Set, Newspaper) when all contents are on_tape, on_disk or completed. |
