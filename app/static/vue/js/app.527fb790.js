(function(e){function a(a){for(var n,o,l=a[0],r=a[1],d=a[2],u=0,m=[];u<l.length;u++)o=l[u],Object.prototype.hasOwnProperty.call(i,o)&&i[o]&&m.push(i[o][0]),i[o]=0;for(n in r)Object.prototype.hasOwnProperty.call(r,n)&&(e[n]=r[n]);c&&c(a);while(m.length)m.shift()();return s.push.apply(s,d||[]),t()}function t(){for(var e,a=0;a<s.length;a++){for(var t=s[a],n=!0,l=1;l<t.length;l++){var r=t[l];0!==i[r]&&(n=!1)}n&&(s.splice(a--,1),e=o(o.s=t[0]))}return e}var n={},i={app:0},s=[];function o(a){if(n[a])return n[a].exports;var t=n[a]={i:a,l:!1,exports:{}};return e[a].call(t.exports,t,t.exports,o),t.l=!0,t.exports}o.m=e,o.c=n,o.d=function(e,a,t){o.o(e,a)||Object.defineProperty(e,a,{enumerable:!0,get:t})},o.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},o.t=function(e,a){if(1&a&&(e=o(e)),8&a)return e;if(4&a&&"object"===typeof e&&e&&e.__esModule)return e;var t=Object.create(null);if(o.r(t),Object.defineProperty(t,"default",{enumerable:!0,value:e}),2&a&&"string"!=typeof e)for(var n in e)o.d(t,n,function(a){return e[a]}.bind(null,n));return t},o.n=function(e){var a=e&&e.__esModule?function(){return e["default"]}:function(){return e};return o.d(a,"a",a),a},o.o=function(e,a){return Object.prototype.hasOwnProperty.call(e,a)},o.p="/";var l=window["webpackJsonp"]=window["webpackJsonp"]||[],r=l.push.bind(l);l.push=a,l=l.slice();for(var d=0;d<l.length;d++)a(l[d]);var c=r;s.push([0,"chunk-vendors"]),t()})({0:function(e,a,t){e.exports=t("56d7")},"034f":function(e,a,t){"use strict";t("85ec")},"080a":function(e,a,t){"use strict";t("a612")},"0d67":function(e,a,t){"use strict";t("e2fe")},"14dd":function(e,a,t){},"569e":function(e,a,t){"use strict";t("85ef")},"56d7":function(e,a,t){"use strict";t.r(a);t("e260"),t("e6cf"),t("cca6"),t("a79d");var n=t("2b0e"),i=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"app"}},[t("LomSection")],1)},s=[],o=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"lom1_section_wrapper"},[t("h2",{staticClass:"title is-clickable",on:{click:e.toggleCollapse}},[e._v(" Leerobject "),t("CollapseIcon",{attrs:{minimized:e.isMinimized}})],1),t("hr"),t("div",{class:{minimized:e.isMinimized},attrs:{id:"lom1_section_block"}},[t("div",{staticClass:"field is-horizontal"},[e._m(0),t("div",{staticClass:"field-body"},[t("TypeSelector")],1)]),t("div",{staticClass:"field is-horizontal"},[e._m(1),t("div",{staticClass:"field-body"},[t("EindgebruikerSelector")],1)]),t("div",{staticClass:"field is-horizontal"},[e._m(2),t("div",{staticClass:"field-body"},[t("TalenSelector")],1)]),t("div",{staticClass:"field is-horizontal"},[e._m(3),t("div",{staticClass:"field-body"},[t("OnderwijsniveausSelector")],1)]),t("div",{staticClass:"field is-horizontal"},[e._m(4),t("div",{staticClass:"field-body"},[t("OnderwijsgradenSelector")],1)]),t("div",{staticClass:"field is-horizontal"},[e._m(5),t("div",{staticClass:"field-body"},[t("ThemaSelector")],1)]),t("div",{staticClass:"field is-horizontal"},[e._m(6),t("div",{staticClass:"field-body"},[t("VakkenSelector")],1)]),t("div",{staticClass:"field is-horizontal"},[e._m(7),t("div",{staticClass:"field-body"},[t("TrefwoordenSelector")],1)])])])},l=[function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label"},[e._v("Type")])])},function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label label-two-lines"},[e._v("Beoogde eindgebruiker")])])},function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label"},[e._v("Taal")])])},function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label"},[e._v("Onderwijsniveaus")])])},function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label"},[e._v("Onderwijsgraden")])])},function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label"},[e._v("Thema")])])},function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label"},[e._v("Vakken")])])},function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"field-label is-normal"},[t("label",{staticClass:"label"},[e._v("Trefwoorden")])])}],r=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"talen_selector"}},[t("multiselect",{attrs:{placeholder:"Kies media type",label:"name","track-by":"code",options:e.options,multiple:!1,taggable:!1,searchable:!1,"show-labels":!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[t("template",{slot:"noResult"},[e._v("Media type niet gevonden")])],2),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"item_type",id:"type_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}}),t("pre",{staticClass:"language-json",attrs:{id:"type_value_preview"}},[t("code",[e._v(e._s(e.value))])])],1)},d=[],c=(t("e9c4"),t("8e5f")),u=t.n(c),m=null,v={name:"TypeSelector",components:{Multiselect:u.a},data:function(){return{value:m,json_value:JSON.stringify(m),options:[{name:"Video",code:"Video"},{name:"Audio",code:"Audio"}]}},created:function(){var e=document.getElementById("item_type");if(e){var a=e.innerText;a&&(m=[{name:a,code:a}],this.json_value=JSON.stringify(m),this.value=m)}},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},h=v,_=(t("60bc"),t("0d67"),t("2877")),f=Object(_["a"])(h,r,d,!1,null,null,null),p=f.exports,g=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"eindgebruikers_selector"}},[t("multiselect",{attrs:{placeholder:"Kies eindgebruikers",label:"name","track-by":"code",options:e.options,multiple:!0,searchable:!1,taggable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[t("template",{slot:"noResult"},[e._v("Beoogde eindgebruiker niet gevonden")])],2),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"lom1_beoogde_eindgebruiker",id:"eindgebruikers_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},k=[],b=[],w={name:"EindgebruikerSelector",components:{Multiselect:u.a},data:function(){return{value:b,json_value:JSON.stringify(b),options:[{name:"Docent",code:"Docent"},{name:"Student",code:"Student"},{name:"Directie",code:"Directie"},{name:"ICT-coördinator",code:"ICT-coördinator"},{name:"Systeembeheerder",code:"Systeembeheerder"},{name:"Preventieadviseur",code:"Preventieadviseur"},{name:"GOK",code:"GOK / Zorgcoördinator"},{name:"Pedagogisch begeleider",code:"Pedagogisch begeleider"},{name:"Inspectielid",code:"Inspectielid"},{name:"Administratief personeel",code:"Administratief personeel"},{name:"Met pensioen",code:"Met pensioen"},{name:"Ouder",code:"Ouder"},{name:"Ander",code:"Ander"}]}},created:function(){var e=document.getElementById("item_eindgebruikers");if(e){var a=JSON.parse(e.innerText);for(var t in a){var n=a[t];b.push({name:n["value"],code:n["value"]})}}this.json_value=JSON.stringify(b)},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},y=w,C=(t("92cc"),Object(_["a"])(y,g,k,!1,null,null,null)),j=C.exports,S=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"talen_selector"}},[t("multiselect",{attrs:{placeholder:"Zoek taal",label:"name","track-by":"code",options:e.options,multiple:!0,taggable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[t("template",{slot:"noResult"},[e._v("Taal niet gevonden")])],2),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"talen",id:"talen_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}}),t("pre",{staticClass:"language-json",attrs:{id:"talen_value_preview"}},[t("code",[e._v(e._s(e.value))])])],1)},O=[],T=(t("b0c0"),[]),E={name:"TalenSelector",components:{Multiselect:u.a},data:function(){return{value:T,json_value:JSON.stringify(T),options:[{name:"Nederlands",code:"nl"},{name:"Frans",code:"fr"},{name:"Duits",code:"de"},{name:"Italiaans",code:"it"},{name:"Engels",code:"en"},{name:"Spaans",code:"es"},{name:"Afar",code:"aa"},{name:"Abchazisch",code:"ab"},{name:"Afrikaans",code:"af"},{name:"Amhaars",code:"am"},{name:"Arabisch",code:"ar"},{name:"Assamees",code:"as"},{name:"Aymara",code:"ay"},{name:"Azerbeidzjaans",code:"az"},{name:"Basjkir",code:"ba"},{name:"Wit-Russisch",code:"be"},{name:"Bislama",code:"bi"},{name:"Bengaals",code:"bn"},{name:"Tibetaans",code:"bo"},{name:"Bretons",code:"br"},{name:"Catalaans",code:"ca"},{name:"Tsjechisch",code:"cs"},{name:"Welch",code:"cy"},{name:"Deens",code:"da"},{name:"Bhutani",code:"dz"},{name:"Grieks",code:"el"},{name:"Esperanto",code:"eo"},{name:"Ests",code:"et"},{name:"Baskisch",code:"eu"},{name:"Perzisch",code:"fa"},{name:"Fins",code:"fi"},{name:"Fiji",code:"fj"},{name:"Iers",code:"ga"},{name:"Schots Gaelic",code:"gd"},{name:"Galicisch",code:"gl"},{name:"Guarani",code:"gn"},{name:"Gujarati",code:"gu"},{name:"Hausa",code:"ha"},{name:"Hebreeuws",code:"he"},{name:"Hindi",code:"hi"},{name:"Hongaars",code:"hu"},{name:"Kroatisch",code:"hr"},{name:"Hongaars",code:"hu"},{name:"Armeens",code:"hy"},{name:"Interlingua",code:"ia"},{name:"Indonesisch",code:"id"},{name:"Interlingue",code:"ie"},{name:"Inupiak",code:"ik"},{name:"IJslands",code:"is"},{name:"Inuktitut (Eskimo)",code:"iu"},{name:"Japans",code:"ja"},{name:"Georgisch",code:"ka"},{name:"Kazachs",code:"kk"},{name:"Groenlands",code:"kl"},{name:"Cambodjaans",code:"km"},{name:"Kannada",code:"kn"},{name:"Koreaans",code:"ko"},{name:"Kasjmir",code:"ks"},{name:"Koerdisch",code:"ku"},{name:"Kirgizisch",code:"ky"},{name:"latijns",code:"la"},{name:"Lingala",code:"ln"},{name:"Laotiaans",code:"lo"},{name:"Litouws",code:"lt"},{name:"Lets, Lets",code:"lv"},{name:"Malagasi",code:"mg"},{name:"Macedonisch",code:"mk"},{name:"Malayalam",code:"ml"},{name:"Mongools",code:"mn"},{name:"Marathi",code:"mr"},{name:"Maleis",code:"ms"},{name:"Maltees",code:"mt"},{name:"Birmaans",code:"my"},{name:"Nauru",code:"na"},{name:"Nepalees",code:"ne"},{name:"Noors",code:"no"},{name:"Occitaans",code:"oc"},{name:"(Afan) Oromo",code:"om"},{name:"Oriya",code:"or"},{name:"Punjabi",code:"pa"},{name:"Pools",code:"pl"},{name:"Pashto, Pushto",code:"ps"},{name:"Portugees",code:"pt"},{name:"Quechua",code:"qu"},{name:"Reto-Romaans",code:"rm"},{name:"Kirundi",code:"rn"},{name:"Roemeens",code:"ro"},{name:"Russisch",code:"ru"},{name:"Kinyarwanda",code:"rw"},{name:"Sanskriet",code:"sa"},{name:"Sindhi",code:"sd"},{name:"Sangro",code:"sg"},{name:"Servo-Kroatisch",code:"sh"},{name:"Singalees",code:"si"},{name:"Slowaaks",code:"sk"},{name:"Sloveens",code:"sl"},{name:"Samoaans",code:"sm"},{name:"Shona",code:"sn"},{name:"Somalisch",code:"so"},{name:"Albanees",code:"sq"},{name:"Servisch",code:"sr"},{name:"Siswati",code:"ss"},{name:"Sesotho",code:"st"},{name:"Soedanees",code:"su"},{name:"Zweeds",code:"sv"},{name:"Swahili",code:"sw"},{name:"Tamil",code:"ta"},{name:"Telugu",code:"te"},{name:"Tadzjieks",code:"tg"},{name:"Thais",code:"th"},{name:"Tigrinya",code:"ti"},{name:"Turkmeens",code:"tk"},{name:"Tagalog",code:"tl"},{name:"Setswana",code:"tn"},{name:"Tonga",code:"to"},{name:"Turks",code:"tr"},{name:"Tsonga",code:"ts"},{name:"Tataars",code:"tt"},{name:"twee keer",code:"tw"},{name:"Oeigoers",code:"ug"},{name:"Oekraïens",code:"uk"},{name:"Urdu",code:"ur"},{name:"Oezbeeks",code:"uz"},{name:"Vietnamees",code:"vi"},{name:"Volapuk",code:"vo"},{name:"Wolof",code:"wo"},{name:"Xhosa",code:"xh"},{name:"Jiddisch",code:"yi"},{name:"Yoruba",code:"yo"},{name:"Zhuang",code:"za"},{name:"Chinees",code:"zh"},{name:"Zulu",code:"zu"}]}},created:function(){var e=document.getElementById("item_languages");if(e){var a=JSON.parse(e.innerText);for(var t in a){var n=a[t]["value"],i="todo";for(var s in this.options){var o=this.options[s];if(o["code"]==n){i=o["name"];break}}T.push({name:i,code:n})}}this.json_value=JSON.stringify(T)},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},N=E,x=(t("b486"),Object(_["a"])(N,S,O,!1,null,null,null)),I=x.exports,V=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"onderwijsniveaus_selector"}},[t("multiselect",{attrs:{placeholder:"Selecteer onderwijsniveaus",label:"label","track-by":"id",options:e.options,multiple:!0,searchable:!1,taggable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[t("template",{slot:"noResult"},[e._v("Onderwijsniveau niet gevonden")])],2),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"lom1_beoogde_eindgebruiker",id:"onderwijsniveaus_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},J=[],z=t("bc3a"),A=t.n(z),M=[],R={name:"OnderwijsniveausSelector",components:{Multiselect:u.a},data:function(){return{value:M,json_value:JSON.stringify(M),options:[{id:"",label:"Onderwijsniveaus inladen...",definition:"Onderwijsniveaus inladen..."}]}},created:function(){var e=this,a="http://localhost:5000",t=document.getElementById("redactie_api_url");t&&(a=t.innerText,A.a.get(a+"/onderwijsniveaus").then((function(a){e.options=a.data;var t=document.getElementById("item_onderwijsniveaus");if(t){var n=JSON.parse(t.innerText),i={},s={};if(n["show_legacy"]){console.log("legacy fallback voor onderwijsniveaus (lom_context)...");var o=document.getElementById("item_onderwijsniveaus_legacy");if(o){var l=JSON.parse(o.innerText);for(var r in l)for(var d in i["definition"]=l[r]["value"],e.options)if(s=e.options[d],i["definition"]==s["definition"]){i["id"]=s["id"],i["label"]=s["label"],M.push({id:i["id"],label:i["label"],definition:i["definition"]});break}}}else for(var c in console.log("loading new onderwijsniveaus from (lom_onderwijsniveau)..."),n)for(var u in i["id"]=n[c]["value"],e.options)if(s=e.options[u],i["id"]==s["id"]){i["label"]=s["label"],i["definition"]=s["definition"],M.push({id:i["id"],label:i["label"],definition:i["definition"]});break}}})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},$=R,B=(t("a304"),Object(_["a"])($,V,J,!1,null,null,null)),P=B.exports,G=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"onderwijsgraden_selector"}},[t("multiselect",{attrs:{placeholder:"Selecteer onderwijsgraden",label:"label","track-by":"id",options:e.options,multiple:!0,taggable:!1,searchable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[t("template",{slot:"noResult"},[e._v("Onderwijsgraad niet gevonden")])],2),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"lom1_onderwijsgraden",id:"onderwijsgraden_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},L=[],K=[],H={name:"OnderwijsgradenSelector",components:{Multiselect:u.a},data:function(){return{value:K,json_value:JSON.stringify(K),options:[{id:"loading...",label:"Onderwijsgraden inladen...",definition:"Onderwijsgraden inladen..."}]}},created:function(){var e=this,a="http://localhost:5000",t=document.getElementById("redactie_api_url");t&&(a=t.innerText,A.a.get(a+"/onderwijsgraden").then((function(a){e.options=a.data;var t=document.getElementById("item_onderwijsgraden");if(t){var n=JSON.parse(t.innerText),i={};if(t&&n["show_legacy"]){console.log("legacy fallback voor onderwijsgraden (lom_typicalagerange)...");var s=document.getElementById("item_onderwijsgraden_legacy");if(s){var o=JSON.parse(s.innerText),l={};for(var r in o){var d=o[r]["value"];for(var c in l["definition"]=d,e.options)if(i=e.options[c],l["definition"]==i["definition"]){l["id"]=i["id"],l["label"]=i["label"],K.push({id:l["id"],label:l["label"],definition:l["definition"]});break}}}}else for(var u in console.log("loading new onderwijsgraden from (lom_onderwijsgraad)..."),n)for(var m in l["id"]=n[u]["value"],e.options)if(i=e.options[m],l["id"]==i["id"]){l["label"]=i["label"],l["definition"]=i["definition"],K.push({id:l["id"],label:l["label"],definition:l["definition"]});break}e.$root.$emit("graden_changed",K)}})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e),this.$root.$emit("graden_changed",e)}}},D=H,F=(t("f329"),Object(_["a"])(D,G,L,!1,null,null,null)),Z=F.exports,W=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"thema_selector"}},[t("multiselect",{attrs:{"tag-placeholder":"Voeg nieuw thema toe",placeholder:"Zoek thema",label:"label","track-by":"id",options:e.options,"option-height":104,"show-labels":!1,multiple:!0,taggable:!1},on:{input:e.updateValue},scopedSlots:e._u([{key:"singleLabel",fn:function(a){return[t("span",{staticClass:"option__desc"},[t("span",{staticClass:"option__title"},[e._v(" "+e._s(a.option.label)+" ")]),t("span",{staticClass:"option_small"},[e._v(" "+e._s(a.option.definition)+" ")])])]}},{key:"option",fn:function(a){return[t("div",{staticClass:"option__desc"},[t("span",{staticClass:"option__title"},[e._v(e._s(a.option.label))]),t("span",{staticClass:"option__small"},[e._v(e._s(a.option.definition))])])]}}]),model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[t("template",{slot:"noResult"},[e._v("Thema niet gevonden")])],2),t("a",{staticClass:"button is-link is-small toon-themas-button",on:{click:e.toggleThemas}},[e._v(" "+e._s(e.show_themas_label)+" ")]),t("div",{staticClass:"thema-search",class:[e.show_thema_cards?"show":"hide"]},[t("div",{staticClass:"field has-addons"},[t("div",{staticClass:"control"},[t("input",{directives:[{name:"model",rawName:"v-model",value:e.thema_search,expression:"thema_search"}],staticClass:"input is-small",attrs:{type:"text",placeholder:"Zoek thema"},domProps:{value:e.thema_search},on:{keydown:function(a){return!a.type.indexOf("key")&&e._k(a.keyCode,"enter",13,a.key,"Enter")?null:e.zoekThemas(a)},input:function(a){a.target.composing||(e.thema_search=a.target.value)}}})]),t("div",{staticClass:"control"},[t("a",{staticClass:"button is-info is-small",on:{click:function(a){return e.zoekThemas(a)}}},[e._v(" Zoek ")])])])]),t("div",{staticClass:"thema-warning-pill",class:[e.show_already_added_warning?"show":"hide"]},[e._v(" Thema werd al toegevoegd ")]),t("div",{staticClass:"thema-cards",class:[e.show_thema_cards?"show":"hide"]},[e.thema_cards.length?e._e():t("div",{staticClass:"notification is-info is-light"},[e._v(' Geen themas gevonden met de zoekterm "'+e._s(e.thema_prev_search)+'". ')]),e._l(e.thema_cards,(function(a,n){return t("div",{key:n,staticClass:"columns"},e._l(a,(function(a){return t("div",{key:a.id,staticClass:"column is-one-quarter"},[t("div",{staticClass:"tile is-ancestor"},[t("div",{staticClass:"tile is-vertical mr-2 mt-2"},[t("div",{staticClass:"card"},[t("header",{staticClass:"card-header",class:[e.themaIsSelected(a)?"thema-selected":""]},[t("p",{staticClass:"card-header-title"},[e._v(" "+e._s(a.label)+" ")])]),t("div",{staticClass:"card-content"},[e._v(" "+e._s(a.definition)+" ")]),t("footer",{staticClass:"card-footer"},[t("a",{staticClass:"card-footer-item",on:{click:function(t){return e.addThema(a)}}},[e._v("Selecteer")])])])])])])})),0)}))],2),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"themas",id:"thema_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},q=[],U=(t("caad"),t("2532"),[]),Q={name:"ThemaSelector",components:{Multiselect:u.a},data:function(){return{value:U,json_value:JSON.stringify(U),options:[{id:"",label:"Themas inladen...",definition:"Themas inladen..."}],thema_cards:[],show_thema_cards:!1,show_already_added_warning:!1,show_themas_label:"Toon themas",thema_search:"",thema_prev_search:""}},created:function(){var e=this,a="http://localhost:5000",t=document.getElementById("redactie_api_url");t&&(a=t.innerText,A.a.get(a+"/themas").then((function(a){for(var t in e.options=[],a.data){var n=a.data[t];n.label.length>1&&e.options.push(n)}})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e),this.$root.$emit("themas_changed",e)},zoekThemas:function(e){this.thema_cards=[];var a=[];for(var t in this.options){var n=this.options[t],i=this.thema_search.toLowerCase(),s=n.label.toLowerCase(),o=n.definition.toLowerCase();(s.includes(i)||o.includes(i))&&a.push(n),4==a.length&&(this.thema_cards.push(a),a=[])}a.length>0&&this.thema_cards.push(a),this.thema_prev_search=this.thema_search,this.thema_search="",e.preventDefault()},themaIsSelected:function(e){for(var a in this.value){var t=this.value[a];if(e.id==t.id)return!0}return!1},toggleThemas:function(){this.show_thema_cards=!this.show_thema_cards,this.show_thema_cards?this.show_themas_label="Verberg themas":(this.show_themas_label="Toon themas",this.thema_cards=[]),this.thema_cards=[];var e=[];for(var a in this.options)e.push(this.options[a]),4==e.length&&(this.thema_cards.push(e),e=[]);e.length>0&&this.thema_cards.push(e)},addThema:function(e){var a=this;console.log("addThema thema=",e);var t=!1;for(var n in this.value){var i=this.value[n];if(i.id==e.id){t=!0;break}}if(t)this.show_already_added_warning=!0,setTimeout((function(){a.show_already_added_warning=!1}),3e3);else{var s={id:e.id,label:e.label,definition:e.definition};this.options.push(s),this.value.push(s),this.json_value=JSON.stringify(this.value),this.$root.$emit("themas_changed",this.value)}}}},X=Q,Y=(t("7b46"),Object(_["a"])(X,W,q,!1,null,null,null)),ee=Y.exports,ae=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"vakken_selector"}},[t("multiselect",{attrs:{id:"vakken_multiselect","tag-placeholder":"Kies vakken",placeholder:"Zoek vak",label:"label","track-by":"id",options:e.options,multiple:!0,taggable:!1},on:{input:e.updateValue},scopedSlots:e._u([{key:"singleLabel",fn:function(a){return[t("span",{staticClass:"option__desc"},[t("span",{staticClass:"option__title"},[e._v(" "+e._s(a.option.label)+" ")]),t("span",{staticClass:"option_small"},[e._v(" "+e._s(a.option.definition)+" ")])])]}},{key:"option",fn:function(a){return[t("div",{staticClass:"option__desc"},[t("span",{staticClass:"option__title"},[e._v(e._s(a.option.label))]),t("span",{staticClass:"option__small"},[e._v(e._s(a.option.definition))])])]}}]),model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[t("template",{slot:"noResult"},[e._v("Vak niet gevonden")])],2),t("a",{staticClass:"button is-link is-small vakken-suggest-button",on:{click:e.toggleSuggesties}},[e._v(" "+e._s(e.suggestie_btn_label)+" ")]),t("div",{staticClass:"vak-warning-pill",class:[e.show_already_added_warning?"show":"hide"]},[e._v(" Vak werd al toegevoegd ")]),t("div",{staticClass:"vakken-suggesties",class:[e.show_vakken_suggesties?"show":"hide"]},[t("h3",{staticClass:"subtitle vakken-title"},[e._v("Suggesties voor vakken")]),e._l(e.vakken_suggesties,(function(a,n){return t("div",{key:"vak"+n,staticClass:"columns"},e._l(a,(function(a){return t("div",{key:a.id,staticClass:"column is-one-quarter"},[t("div",{staticClass:"tile is-ancestor"},[t("div",{staticClass:"tile is-vertical mr-2 mt-2"},[t("div",{staticClass:"card"},[t("header",{staticClass:"card-header",class:[e.vakIsSelected(a)?"vak-selected":""]},[t("p",{staticClass:"card-header-title"},[e._v(" "+e._s(a.label)+" ")])]),t("div",{staticClass:"card-content"},[e._v(" "+e._s(a.definition)+" ")]),t("footer",{staticClass:"card-footer"},[t("a",{staticClass:"card-footer-item",on:{click:function(t){return e.addVakSuggestie(a)}}},[e._v("Selecteer")])])])])])])})),0)})),t("h3",{staticClass:"subtitle vakken-title"},[e._v("Overige vakken")]),e._l(e.overige_vakken,(function(a,n){return t("div",{key:"sug"+n,staticClass:"columns"},e._l(a,(function(a){return t("div",{key:a.id,staticClass:"column is-one-quarter"},[t("div",{staticClass:"tile is-ancestor"},[t("div",{staticClass:"tile is-vertical mr-2 mt-2"},[t("div",{staticClass:"card"},[t("header",{staticClass:"card-header",class:[e.vakIsSelected(a)?"vak-selected":""]},[t("p",{staticClass:"card-header-title"},[e._v(" "+e._s(a.label)+" ")])]),t("div",{staticClass:"card-content"},[e._v(" "+e._s(a.definition)+" ")]),t("footer",{staticClass:"card-footer"},[t("a",{staticClass:"card-footer-item",on:{click:function(t){return e.addVakSuggestie(a)}}},[e._v("Selecteer")])])])])])])})),0)}))],2),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"vakken",id:"vakken_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},te=[],ne=[],ie={name:"VakkenSelector",components:{Multiselect:u.a},props:{},data:function(){return{value:ne,json_value:JSON.stringify(ne),options:[{id:"1",label:"Vakken inladen...",definition:"Vakken inladen..."}],show_vakken_suggesties:!1,show_already_added_warning:!1,suggestie_btn_label:"Toon suggesties voor vakken",vakken_suggesties:[[{id:"2",label:"Suggesties vakken inladen...",definition:"Suggesties vakken definitions inladen..."}]],overige_vakken:[[{id:"3",label:"Overige vakken inladen...",definition:"Overige vakken definitions inladen..."}]],graden:[],themas:[]}},mounted:function(){var e=this;this.$root.$on("graden_changed",(function(a){console.log("graden changed data=",a),e.graden=a})),this.$root.$on("themas_changed",(function(a){console.log("themas changed data=",a),e.themas=a}))},created:function(){var e=this,a="http://localhost:5000",t=document.getElementById("redactie_api_url");t&&(a=t.innerText,A.a.get(a+"/vakken").then((function(a){e.options=a.data})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)},vakIsSelected:function(e){for(var a in this.value){var t=this.value[a];if(e.id==t.id)return!0}return!1},toggleSuggesties:function(){var e=this;this.show_vakken_suggesties=!this.show_vakken_suggesties,this.show_vakken_suggesties?(this.suggestie_btn_label="Verberg suggesties voor vakken",console.log("make axios call here...")):this.suggestie_btn_label="Toon suggesties voor vakken";var a="http://localhost:5000",t=document.getElementById("redactie_api_url");if(t){a=t.innerText;var n={graden:this.graden,themas:this.themas};A.a.post(a+"/vakken_suggest",n).then((function(t){e.vakken_suggesties=[];var n=[],i={};for(var s in t.data){var o=t.data[s];i[o.id]=o,n.push(o),4==n.length&&(e.vakken_suggesties.push(n),n=[])}n.length>0&&e.vakken_suggesties.push(n),console.log("suggest_map=",i),A.a.get(a+"/vakken").then((function(a){e.overige_vakken=[];var t=[];for(var n in a.data){var s=a.data[n];void 0==i[s.id]&&t.push(s),t.length>=4&&(e.overige_vakken.push(t),t=[])}t.length>0&&e.overige_vakken.push(t)}))}))}},addVakSuggestie:function(e){var a=this,t=!1;for(var n in this.value){var i=this.value[n];if(i.id==e.id){t=!0;break}}if(t)this.show_already_added_warning=!0,setTimeout((function(){a.show_already_added_warning=!1}),3e3);else{var s={id:e.id,label:e.label,definition:e.definition};this.options.push(s),this.value.push(s),this.json_value=JSON.stringify(this.value)}}}},se=ie,oe=(t("569e"),Object(_["a"])(se,ae,te,!1,null,null,null)),le=oe.exports,re=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{attrs:{id:"trefwoorden_selector"}},[t("multiselect",{attrs:{"tag-placeholder":"Maak nieuw trefwoord aan",placeholder:"Zoek of voeg een nieuw trefwoord toe",label:"name","track-by":"code",options:e.options,multiple:!0,taggable:!0},on:{tag:e.addTrefwoord,input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}}),t("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"trefwoorden",id:"trefwoorden_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}}),t("div",{staticClass:"cp_keywords_button"},[t("a",{on:{click:e.toggleKeywordCollapse}},[e._v(" "+e._s(e.cp_keyword_label)+" ")]),t("div",{staticClass:"warning-pill",class:[e.show_already_added_warning?"show":"hide"]},[e._v(" Keyword werd al toegevoegd ")])]),t("div",{staticClass:"cp_keywords",class:[e.show_cp_keywords?"show":"hide"]},[e.cp_keywords.length?e._e():t("div",{staticClass:"notification is-info is-light"},[e._v(" Voor dit item zijn er geen Content Partner trefwoorden. ")]),e._l(e.cp_keywords,(function(a){return t("div",{key:a.code,staticClass:"keyword-pill",on:{click:function(t){return e.addCpKeyword(a)}}},[e._v(" "+e._s(a.name)+" ")])}))],2)],1)},de=[],ce=[],ue={name:"TrefwoordenSelector",components:{Multiselect:u.a},props:{},data:function(){return{value:ce,json_value:JSON.stringify(ce),options:[{name:"reportage",code:"reportage"},{name:"Silent Movie",code:"Silent Movie"},{name:"Belgium",code:"Belgium"},{name:"France",code:"France"},{name:"Spain",code:"Spain"},{name:"BURGER",code:"BURGER"},{name:"CONFLICT",code:"CONFLICT"},{name:"CONVENTIE VAN GENEVE",code:"CONVENTIE VAN GENEVE"},{name:"INTERNATIONAAL STRAFGERECHTSHOF",code:"INTERNATIONAAL STRAFGERECHTSHOF"},{name:"MENSENRECHT",code:"MENSENRECHT"},{name:"OORLOG",code:"OORLOG"},{name:"OORLOGSMISDAAD",code:"OORLOGSMISDAAD"},{name:"SCHENDING",code:"SCHENDING"},{name:"STRAFRECHT",code:"STRAFRECHT"},{name:"VAN DEN WIJNGAERT CHRIS",code:"VAN DEN WIJNGAERT CHRIS"},{name:"VEILIGHEID",code:"VEILIGHEID"},{name:"Christiane van den Wijngaert",code:"Christiane van den Wijngaert"},{name:"conventie van Genève",code:"conventie van Genève"},{name:"Internationaal Strafhof",code:"Internationaal Strafhof"},{name:"justitie",code:"justitie"},{name:"mensenrechten",code:"mensenrechten"},{name:"oorlog",code:"oorlog"}],cp_keywords:[],show_cp_keywords:!1,show_already_added_warning:!1,cp_keyword_label:"Bekijk trefwoorden van Content Partners"}},created:function(){var e=document.getElementById("item_keywords");if(e){var a=JSON.parse(e.innerText);for(var t in a){var n=a[t];ce.push({name:n["value"],code:n["value"]})}this.json_value=JSON.stringify(ce)}var i=document.getElementById("item_keywords_cp");if(i){var s=JSON.parse(i.innerText);for(var o in s){var l=s[o];this.cp_keywords.push({name:l["value"],code:l["value"]})}}},methods:{addTrefwoord:function(e){console.log("addTrefwoord nieuw woord=",e);var a={name:e,code:e.substring(0,2)+Math.floor(1e7*Math.random())};this.options.push(a),this.value.push(a),this.json_value=JSON.stringify(this.value)},updateValue:function(e){this.json_value=JSON.stringify(e)},toggleKeywordCollapse:function(){this.show_cp_keywords=!this.show_cp_keywords,this.show_cp_keywords?this.cp_keyword_label="Verberg trefwoorden van Content Partners":this.cp_keyword_label="Bekijk trefwoorden van Content Partners"},addCpKeyword:function(e){var a=this,t=!1;for(var n in this.value){var i=this.value[n];if(i.code==e.code){t=!0;break}}if(t)this.show_already_added_warning=!0,setTimeout((function(){a.show_already_added_warning=!1}),3e3);else{var s={name:e.name,code:e.code};this.options.push(s),this.value.push(s),this.json_value=JSON.stringify(this.value)}}}},me=ue,ve=(t("ea01"),Object(_["a"])(me,re,de,!1,null,null,null)),he=ve.exports,_e=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",{staticClass:"minimize-icon-wrapper"},[t("span",{class:[e.minimized?"icon-folded":"icon-unfolded"]},[t("ion-icon",{staticClass:"md hydrated",attrs:{name:"chevron-down-circle-outline",role:"img","aria-label":"chevron down circle outline"}})],1),t("span",{class:[e.minimized?"icon-unfolded":"icon-folded"]},[t("ion-icon",{staticClass:"md hydrated",attrs:{name:"chevron-forward-circle-outline",role:"img","aria-label":"chevron forward circle outline"}})],1)])},fe=[],pe={name:"CollapseIcon",components:{},props:{minimized:Boolean},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},ge=pe,ke=(t("c6f0"),Object(_["a"])(ge,_e,fe,!1,null,null,null)),be=ke.exports,we=document.getElementById("pid");if(we){var ye=we.innerText;console.log("LomSection for pid=",ye)}var Ce={name:"LomSection",components:{TypeSelector:p,EindgebruikerSelector:j,TalenSelector:I,OnderwijsniveausSelector:P,OnderwijsgradenSelector:Z,ThemaSelector:ee,VakkenSelector:le,TrefwoordenSelector:he,CollapseIcon:be},data:function(){return{isMinimized:!1,pid:ye}},methods:{toggleCollapse:function(){this.isMinimized=!this.isMinimized}}},je=Ce,Se=(t("080a"),Object(_["a"])(je,o,l,!1,null,null,null)),Oe=Se.exports,Te={name:"App",components:{LomSection:Oe}},Ee=Te,Ne=(t("034f"),Object(_["a"])(Ee,i,s,!1,null,null,null)),xe=Ne.exports;n["a"].config.productionTip=!1,n["a"].config.ignoredElements=[/^ion-/],new n["a"]({render:function(e){return e(xe)}}).$mount("#app")},6586:function(e,a,t){},"68f1":function(e,a,t){},"71d9":function(e,a,t){},"7b46":function(e,a,t){"use strict";t("68f1")},"85ec":function(e,a,t){},"85ef":function(e,a,t){},"90d9":function(e,a,t){},"92cc":function(e,a,t){"use strict";t("b2c9")},"97c9":function(e,a,t){},a304:function(e,a,t){"use strict";t("71d9")},a612:function(e,a,t){},b2c9:function(e,a,t){},b486:function(e,a,t){"use strict";t("97c9")},c6f0:function(e,a,t){"use strict";t("6586")},e2fe:function(e,a,t){},ea01:function(e,a,t){"use strict";t("90d9")},f329:function(e,a,t){"use strict";t("14dd")}});
//# sourceMappingURL=app.527fb790.js.map