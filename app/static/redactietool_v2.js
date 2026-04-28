// ============================== App JavaScript ===============================
// Author: Walter Schreppers
//
//  File: app/static/app.js
//
// Animate submit buttons and handle fixed bulma menu events.
//
// Handle collapsing of sections and adding/removing items
// in productie section metadata form. 
//
// future work: we might split this up in seperate js files and
// have some minification done in our precompile assets makefile target.


function get_id(div_id){
  return document.getElementById(div_id);
}

// ============================ LOGIN/LOGOUT FORMS =============================
function execute(btn, label){
  btn.form.submit(); 
  btn.disabled=true; 
  btn.value=label;
}

function loginSubmit(btn){
  execute(btn, "Authenticeren..."); 
  btn.classList.add('is-loading')
}

function logoutClicked(ref){
  // #logout_btn
  ref.className += ' disabled';
}

function newUploadClicked(ref){
  // #new_upload_btn
  ref.className += ' disabled';
}

function restoreButton(btn_id, btn_label){
  console.log("restoring button=", btn_id);
  btn = get_id(btn_id);
  if(btn){
    btn.disabled=false;
    btn.value=btn_label;
  }
}

function clearButtonLoadingState(){
  restoreButton("btn_metadata_bewerken", "Metadata bewerken");
}

function resetSearch(){
  clearButtonLoadingState();

  setTimeout(function(){
    search_input = get_id("pid_search");
    if(search_input){ 
        console.log("clearing pid_search!");
        search_input.value = "";
    }
  }, 50);

}


// ============================= MODAL DIALOG ==================================
function showNavigationWarning(){
  showModalAlert(
      "Ben je zeker dat je deze pagina wilt verlaten?",
      "Opgelet: je bewerkingen worden niet bewaard wanneer je deze pagina verlaat."
  );
}

function flashModalWarning(){
  showModalAlert(
      "Sync is misgelopen",
      "Deze alert gaat na 3 seconden automatisch dicht..."
  );

  setTimeout(function(){
    closeModalAlert();
  }, 3000);
}


// ============================== SUBTITLE FORMS ===============================
function pidSubmitForMetadata(btn){
  window.localStorage.removeItem("productie_section_opened");
  execute(btn, 'Item opzoeken...');
}

// Preview a locally selected SRT file in the Flowplayer video player
function previewSubtitleInPlayer(input){
  if(!input.files || !input.files[0]) return;

  var previewMsg = document.getElementById('subtitle_preview_msg');
  if(previewMsg) previewMsg.style.display = '';

  var reader = new FileReader();
  reader.onload = function(e){
    var srtText = e.target.result;
    // Convert SRT to WebVTT: add header, replace comma with period in timestamps
    var vttText = "WEBVTT\n\n" + srtText
      .replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g, '$1.$2');

    var blob = new Blob([vttText], {type: 'text/vtt'});
    var blobUrl = URL.createObjectURL(blob);

    // Try to add/replace a <track> element on the underlying <video>
    var video = document.querySelector('#player_container video');
    if(video){
      // Remove any existing preview tracks
      var existingTracks = video.querySelectorAll('track.preview-track');
      existingTracks.forEach(function(t){ t.remove(); });

      var track = document.createElement('track');
      track.className = 'preview-track';
      track.kind = 'subtitles';
      track.label = 'Preview';
      track.srclang = 'nl';
      track.src = blobUrl;
      track.default = true;
      video.appendChild(track);

      // Activate the new track
      for(var i = 0; i < video.textTracks.length; i++){
        video.textTracks[i].mode = (video.textTracks[i].label === 'Preview') ? 'showing' : 'hidden';
      }
    }
  };
  reader.readAsText(input.files[0]);
}


// ============================ METADATA EDIT FORM =============================
// add item method for 'productie' section
function addPrdItem(item_list_id, item_fields_id){
  var item_fields = get_id(item_fields_id);
  if(!item_fields){
    console.log("ERROR in addPrdItem: could not find item_fields_id=", item_fields_id);
    return false;
  }

  var item_list = get_id(item_list_id);
  if(!item_list){
    console.log("ERROR in addPrdItem: could not find item_list_id=", item_list_id);
    return false;
  }

  // add unique ids to _input_ and _value_ fields in cloned element
  var new_id = 1;
  var item_inputs = item_list.getElementsByTagName("input");
  if(item_inputs.length){
    var last_id = item_inputs[item_inputs.length-1].id
    if(last_id.includes("_value_")){
      new_id = parseInt(last_id.replace(item_fields_id+'_value_', ''))+1
    }
  }

  var fields_clone = item_fields.cloneNode(true);
  //fields_clone.style.display = 'flex';
  fields_clone.id = fields_clone.id+"_"+new_id;
  fields_clone.getElementsByTagName("select")[0].name = item_fields_id+"_attribute_"+new_id
  fields_clone.getElementsByTagName("select")[0].id = item_fields_id+"_attribute_"+new_id
  fields_clone.getElementsByTagName("input")[0].name = item_fields_id+"_value_"+new_id
  fields_clone.getElementsByTagName("input")[0].id = item_fields_id+"_value_"+new_id

  // now append our cloned fields with unique name+id
  console.log("adding item_fields=", fields_clone);
  item_list.append(fields_clone);
  metadataInputChanged(item_fields_id);
  return false;
}

// delete item method for 'productie' sections
function deletePrdItem(del_btn){
  del_btn.parentNode.parentNode.remove();
  metadataInputChanged('deleted_production_item');
  return false;
}

function closeSection(section_div_id){
  var form_section = get_id(section_div_id);
  if(!form_section) return;
  var close_icon_wrapper = get_id(section_div_id + "_icon");
  var folded_icon = close_icon_wrapper.getElementsByClassName("icon-folded")[0];
  var unfolded_icon = close_icon_wrapper.getElementsByClassName("icon-unfolded")[0];

  form_section.style.display="none";
  unfolded_icon.style.display="none";
  folded_icon.style.display="block";
}

function openSection(section_div_id){
  var form_section = get_id(section_div_id);
  if(!form_section) return;
  var close_icon_wrapper = get_id(section_div_id + "_icon");
  var folded_icon = close_icon_wrapper.getElementsByClassName("icon-folded")[0];
  var unfolded_icon = close_icon_wrapper.getElementsByClassName("icon-unfolded")[0];

  form_section.style.display="block";
  unfolded_icon.style.display="block";
  folded_icon.style.display="none";
}

function sectionToggle(section_div_id){
  var form_section = get_id(section_div_id);
  if(!form_section) return;
 
  if(form_section.style.display == 'none'){
    if(section_div_id=="productie_section"){
      window.localStorage.setItem("productie_section_opened", "true");
    }
    openSection(section_div_id);
  }
  else{
    if(section_div_id=="productie_section"){
      window.localStorage.removeItem("productie_section_opened");
    }

    closeSection(section_div_id);
  }
}

function updateProductionSection(){
  // use localstorage to keep state of opened production section
  if(window.localStorage.getItem("productie_section_opened") == "true"){
    openSection("productio_section");
  }
  else{
    closeSection("productie_section");
  }
}

function collapseEmptyTextarea(area_id, uncollapsable=false){
  var ta = get_id(area_id);
  if( ta && ta.innerHTML.length == 0){
    if(uncollapsable){
      ta.parentNode.parentNode.style.display="none";
    }
    else{
      ta.parentNode.parentNode.parentNode.style.display="none";
    }
  }
}

// Inhoud section hide unused/empty textarea's for current item
function collapseEmptyTextareas(){
  // when passing 'true' we show a collapse/uncollapse icon and 
  // keep the heading in our section around the textarea when its collapsed
  // collapseEmptyTextarea("originele_hoofdbeschrijving", true);
  collapseEmptyTextarea("originele_hoofdbeschrijving");
  collapseEmptyTextarea("originele_uitgebreide_hoofdbeschrijving");
  collapseEmptyTextarea("ondertitels");
  collapseEmptyTextarea("programma_beschrijving");
  collapseEmptyTextarea("cast");
  collapseEmptyTextarea("transcriptie");
}

function hideEmptyTitleInput(input_id){
  var input_field = get_id(input_id);
  if( input_field ){
    var input_box = input_field.getElementsByTagName("input")[0];
    if( input_box && input_box.value.length == 0){
      input_field.style.display = "none";
    }
    else{
      input_field.style.display = "flex";
    }
  }
}

function hideEmptyTitles(){
  hideEmptyTitleInput("titel_episode")
  hideEmptyTitleInput("titel_aflevering");
  hideEmptyTitleInput("titel_alternatief");
  hideEmptyTitleInput("titel_programma");
  hideEmptyTitleInput("titel_serienummer");
  hideEmptyTitleInput("titel_seizoen");
  hideEmptyTitleInput("titel_seizoen_nummer");
  hideEmptyTitleInput("titel_archief");
  hideEmptyTitleInput("titel_deelarchief");
  hideEmptyTitleInput("titel_reeks");
  hideEmptyTitleInput("titel_deelreeks");
  hideEmptyTitleInput("titel_registratie");
}


function showTitleInput(input_id){
  var input_field = get_id(input_id);
  if( input_field ){
    input_field.style.display = "flex";
  }
}

function showEmptyTitles(){
  showTitleInput("titel_episode")
  showTitleInput("titel_aflevering");
  showTitleInput("titel_alternatief");
  showTitleInput("titel_programma");
  showTitleInput("titel_serienummer");
  showTitleInput("titel_seizoen");
  showTitleInput("titel_seizoen_nummer");
  showTitleInput("titel_archief");
  showTitleInput("titel_deelarchief");
  showTitleInput("titel_reeks");
  showTitleInput("titel_deelreeks");
  showTitleInput("titel_registratie");
}

function closeAlert(box_id){
  var alert_box = get_id(box_id);
  if(alert_box){
    alert_box.classList.remove("fadein");
    alert_box.classList.add("fadeout");
    setTimeout(function(){
      alert_box.style.display = "none";
    }, 400);
  }
}

function autoCloseAlert(box_id){
  var alert_box = get_id(box_id);
  if(alert_box){
    setTimeout(function(){
      closeAlert(box_id);
    }, 4000); 
  }
}

function refreshKeyframeImage(img_id){
  console.log("can be added later if mediahaven changes the previewImageUrl on keyframe change...");
  // we need to reload the background image url by finding flowplayer's id and then going down
  // in dom and update background tag.
}

function injectApiUrl(url_div_id){
  var api_url_div = get_id('redactie_api_url');
  if(api_url_div){
    api_url_div.innerText = window.location.protocol+'//'+window.location.host;
  }
  else{
    console.log("Warning could not inject api url into div=", url_div_id);
  }
}

function isValidDate(dateString) {
  var reg_ex = /^\d{4}-\d{2}-\d{2}$/;
  if(!dateString.match(reg_ex)) return false;  // Invalid format
  var d = new Date(dateString);
  var ts = d.getTime();
  if(!ts && ts !== 0) return false; // NaN, invalid timestamp
  return d.toISOString().substr(0,10) === dateString;
}

function checkDate(date_id){
  var date_div = get_id(date_id)
  if(!date_div) return;

  var valid = isValidDate(date_div.value);
  var error_div = get_id(date_id+"_error");
  if(!valid){ //show error
    date_div.classList.add("is-danger");
    if(error_div) error_div.classList.remove("hidden");
  }
  else{
    date_div.classList.remove("is-danger");
    if(error_div) error_div.classList.add("hidden");
  }
}

function checkDateInput(date_id){
  checkDate(date_id); 
  metadataInputChanged(date_id);
}

function checkDateInputs(){
  // checkDate("creatiedatum"); // per request disable checks here
  checkDate("uitzenddatum");
}

function metadataInputChanged(name){
  edited = get_id("metadata_form_edited");
  edited.value = "true";
}

function metadataFormEdited(){
  edited = get_id("metadata_form_edited");
  if(edited){
    return edited.value == "true"
  }
  else{
    return false;
  }
}

function checkMetadataSaved(event) {
  if(metadataFormEdited()){
    console.log("edited == true, warning dialog !!!");
    // shows native dialog with warning you close or navigate away
    event.returnValue = "Opgelet: je bewerkingen worden niet bewaard wanneer je deze pagina verlaat.";
  }
  else{
    delete event['returnValue']; // cancel native dialog
  }
}

function metadataSubmit(btn){
  edited = get_id("metadata_form_edited");
  edited.value = "false";
  btn.classList.add('is-loading');
  btn.form.submit();
}

function resetMetadataSubmit(){
  console.log("reset submit");
  btn = get_id("metadata_submit_btn");
  if(btn) btn.classList.remove('is-loading');
}

// =========================== DOCUMENT READY EVENT ============================
// Handle burger menu open/close on all pages.
// Handle collapsing and hiding of inputs, textareas 
// and notifications on the metadata edit form
// Handle any other resetting of state on pageload if necessary
document.addEventListener('DOMContentLoaded', () => {

  // Get all "navbar-burger" elements
  const navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll('.navbar-burger'), 0
  );

  // Check if there are any navbar burgers
  if (navbarBurgers.length > 0) {
    // Add a click event on each of them
    navbarBurgers.forEach( el => {
      el.addEventListener('click', () => {
        // Get the target from the "data-target" attribute
        const data_target = el.dataset.target;
        const target = get_id(data_target);

        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        el.classList.toggle('is-active');
        target.classList.toggle('is-active');
      });
    });
  }

  console.log("dom ready event fired!");
  collapseEmptyTextareas();
  hideEmptyTitles();
  updateProductionSection();
  closeSection("upload_info_section");
  autoCloseAlert("alert_box");
  autoCloseAlert("data_saved_alert_box");
  checkDateInputs(); 
  resetSearch();
  resetMetadataSubmit();
 });


// force dom ready with back button
window.addEventListener('unload', function(){
  resetSearch();
  resetMetadataSubmit();
});

// show navigation dialog on metadata edit after editing
window.addEventListener('beforeunload', checkMetadataSaved);


