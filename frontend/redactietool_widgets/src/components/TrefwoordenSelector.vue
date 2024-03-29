<template>
  <div id="trefwoorden_selector">

    <multiselect v-model="value" 
      tag-placeholder="Maak nieuw trefwoord aan" 
      select-label="Selecteer trefwoord"
      deselect-label="Verwijder trefwoord"
      :show-labels="false"
      :blockKeys="['Delete']"
      :hide-selected="true"
      :loading="loading"
      placeholder="" 
      label="name" 
      track-by="code" 
      :options="options" :multiple="true"
      @search-change="elasticSearch"
      :taggable="true" @tag="addKeywordDialog" @input="updateValue">

      <span slot="noOptions">Zoek trefwoord</span>
      <span slot="noResult">Trefwoord niet gevonden</span>
    </multiselect>

     
    <textarea name="trefwoorden" v-model="json_value" id="trefwoorden_json_value"></textarea>

    <div class="create-trefwoord" v-bind:class="[show_keyword_dialog? 'show' : 'hide']">
      <div class="modal is-active" id="keyword_modal">
        <div class="modal-background"></div>
        <div class="modal-card" id="keyword_modal_card">
          <header class="modal-card-head">
            <p class="modal-card-title">Nieuw trefwoord</p>
          </header>

          <section class="modal-card-body">
            <p>
              Ben je zeker dat je een volledig nieuw trefwoord wil toevoegen?
            </p>
            <br/>
            <div class="field is-horizontal">
              <div class="field-label is-normal">
                Trefwoord
              </div>

              <div class="field-body">
                <div class="field">
                <div class="control">
                  <input 
                    id="keyword_input"
                    class="input keyword-input" 
                    type="text" 
                    v-model="new_keyword"/>
                </div>
                </div>
              </div>
            </div>
          </section>

          <footer class="modal-card-foot buttons-right">
              <a class="button is-link is-light" 
                v-on:click="cancelKeywordDialog()">
                  Annuleren 
              </a>
              <a class="button is-link" 
                v-on:click="addKeyword(new_keyword)">
                  Toevoegen
              </a>
          </footer>
        </div>
      </div>
    </div>

    <div v-if="cp_keywords.length">
      <div class="cp_keywords_button">
        <a class="" v-on:click="toggleKeywordCollapse">
          {{cp_keyword_label}}
        </a>
        <div class="warning-pill" v-bind:class="[show_already_added_warning ? 'show' : 'hide']">
          Trefwoord werd al toegevoegd.
        </div>
      </div>

      <div class="cp_keywords" v-bind:class="[show_cp_keywords ? 'show' : 'hide']">

        <div v-if="!cp_keywords.length" class="notification is-info is-light">
          Voor dit item zijn er geen contentpartner trefwoorden.
        </div>

        <!-- 
          addinc content parnter keywords has been disabled
          v-on:click="addCpKeyword(keyword)"
        -->
        <div 
          class="keyword-pill is-pulled-left" 
          v-for="keyword in cp_keywords" 
          :key="keyword.code"
          >
          {{keyword.name}}
        </div>
        <div class="is-clearfix"></div>
      </div>
    </div>

  </div>
</template>

<script>
  import Multiselect from 'vue-multiselect'
  import axios from 'axios';

  var default_value = [];
  export default {
    name: 'TrefwoordenSelector',
    components: {
      Multiselect 
    },
    props: {
      metadata: Object
    },
    data () {
      return {
        value: default_value,
        json_value: JSON.stringify(default_value),
        options: [],
        loading: false,
        redactie_api_url: "",
        cp_keyword_label: "Bekijk de trefwoorden van de contentpartner",
        cp_keywords: [],
        show_cp_keywords: false,
        show_already_added_warning: false,
        new_keyword: "",
        show_keyword_dialog: false
      }
    },
    created(){
      if(this.metadata.item_keywords){
        var keywords = this.metadata.item_keywords;
        this.value = [];
        for(var k in keywords){
          var keyword = keywords[k]
          this.value.push(
            {
              'name': keyword['value'],
              'code': keyword['value']
            }
          );
        }
        this.json_value = JSON.stringify(this.value);
      }

      if( this.metadata.item_keywords_cp ){
        var keywords_cp = this.metadata.item_keywords_cp;
        this.cp_keywords = [];
        for(var cpk in keywords_cp){
          var cp_keyword = keywords_cp[cpk]
          this.cp_keywords.push(
            {
              'name': cp_keyword['value'],
              'code': cp_keyword['value']
            }
          );
        }
      }

      // use mocked data on port 5000 during development (run: make vue_develop_api)
      // this.redactie_api_url = 'http://localhost:5000';
      var redactie_api_div = document.getElementById('redactie_api_url');
      if( redactie_api_div ){
        this.redactie_api_url = redactie_api_div.innerText;
      }

    },
    methods: { 
      updateValue(value){
        this.json_value = JSON.stringify(value)
        this.$root.$emit("metadata_edited", "true");
      },
      
      toggleKeywordCollapse(){
        this.show_cp_keywords= !this.show_cp_keywords;
        if(this.show_cp_keywords){
          this.cp_keyword_label = "Verberg de trefwoorden van de contentpartner";
        }
        else{
          this.cp_keyword_label = "Bekijk de trefwoorden van de contentpartner";
        }
      },

      addCpKeyword(kw){
        var already_added = false;

        for( var o in this.value){
          var okw = this.value[o];
          if(okw.code == kw.code){
            already_added = true;
            break;
          } 
        }

        if(!already_added){
          const tw = {
            name: kw.name,
            code: kw.code
          };
          this.options.push(tw);
          this.value.push(tw);
          this.json_value = JSON.stringify(this.value);
        }
        else{
          this.show_already_added_warning = true;
          setTimeout(()=>{
            this.show_already_added_warning = false;
          }, 3000);
        }
      },

      addKeyword(new_keyword) {
        this.show_keyword_dialog=false;
        const tw = {
          name: new_keyword,
          code: new_keyword.substring(0, 2) + Math.floor((Math.random() * 10000000))
        }
        this.options.push(tw)
        this.value.push(tw)
        this.json_value = JSON.stringify(this.value)
        this.$root.$emit("metadata_edited", "true");
      },

      cancelKeywordDialog(){
        this.show_keyword_dialog = false;
      },

      addKeywordDialog(keyword){
        this.new_keyword = keyword;
        this.show_keyword_dialog = true;
        setTimeout(function(){
          document.getElementById("keyword_input").focus();
        }, 100);
      },

      elasticSearch(qry){
        if(qry.length < 3){
          // console.log("not searching, need 3 chars, current qry=", qry);
          this.options = [];
          return
        }
        this.loading = true;
        axios
          .post(this.redactie_api_url+'/keyword_search', {qry: qry})
          .then(res => {
            this.options = [];
            for(var i in res.data){
              var es_result = res.data[i];
              const tw = {
                name: es_result['text'],
                code: es_result['_id']
              };
              this.options.push(tw);
            }
            this.loading = false;
          })
          .catch(error => {
            console.log("keywoard search error=", error.message);
            this.loading = false;
          });
      }
    }
  }
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style>
  #trefwoorden_selector{
    min-width: 25em;
  }
  #trefwoorden_json_value{
    margin-top: 20px;
    margin-bottom: 20px;
    display: flex;
    width: 80%;
    height: 100px;
    display: none;
  }
  .cp_keywords_button {
    margin-top: 10px;
    margin-bottom: 10px;
  }
  .keyword-pill{
    border-radius: 5px;
    border: 1px solid #9cafbd;
    background-color: #edeff2;
    color: #2b414f;
    text-overflow: ellipsis;
    position: relative;
    display: inline-block;
    margin-right: 8px;
    padding: 0px 8px 0px 8px;
    margin-bottom: 5px;
  }
  .warning-pill{
    border-radius: 5px;
    background: #ff6a6a;
    color: #eee;
    display: inline-block;
    text-overflow: ellipsis;
    padding: 2px 8px 2px 13px;
    margin-bottom: 5px;
    width: 15em;
  }
  .hide{
    display: none;
  }
  .show{
    display: block;
  }
  .button.is-link.is-light{
    border-color: #97b8d3 !important;
  }
  .keyword-input{
    border-color: #9cafbd;
  }
  .buttons-right{
    justify-content: flex-end;
  }
</style>
