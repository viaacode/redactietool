(function(e){function a(a){for(var t,o,l=a[0],r=a[1],d=a[2],u=0,m=[];u<l.length;u++)o=l[u],Object.prototype.hasOwnProperty.call(i,o)&&i[o]&&m.push(i[o][0]),i[o]=0;for(t in r)Object.prototype.hasOwnProperty.call(r,t)&&(e[t]=r[t]);c&&c(a);while(m.length)m.shift()();return s.push.apply(s,d||[]),n()}function n(){for(var e,a=0;a<s.length;a++){for(var n=s[a],t=!0,l=1;l<n.length;l++){var r=n[l];0!==i[r]&&(t=!1)}t&&(s.splice(a--,1),e=o(o.s=n[0]))}return e}var t={},i={app:0},s=[];function o(a){if(t[a])return t[a].exports;var n=t[a]={i:a,l:!1,exports:{}};return e[a].call(n.exports,n,n.exports,o),n.l=!0,n.exports}o.m=e,o.c=t,o.d=function(e,a,n){o.o(e,a)||Object.defineProperty(e,a,{enumerable:!0,get:n})},o.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},o.t=function(e,a){if(1&a&&(e=o(e)),8&a)return e;if(4&a&&"object"===typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(o.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&a&&"string"!=typeof e)for(var t in e)o.d(n,t,function(a){return e[a]}.bind(null,t));return n},o.n=function(e){var a=e&&e.__esModule?function(){return e["default"]}:function(){return e};return o.d(a,"a",a),a},o.o=function(e,a){return Object.prototype.hasOwnProperty.call(e,a)},o.p="/";var l=window["webpackJsonp"]=window["webpackJsonp"]||[],r=l.push.bind(l);l.push=a,l=l.slice();for(var d=0;d<l.length;d++)a(l[d]);var c=r;s.push([0,"chunk-vendors"]),n()})({0:function(e,a,n){e.exports=n("56d7")},"034f":function(e,a,n){"use strict";n("85ec")},"080a":function(e,a,n){"use strict";n("a612")},"0d67":function(e,a,n){"use strict";n("e2fe")},"14dd":function(e,a,n){},"569e":function(e,a,n){"use strict";n("85ef")},"56d7":function(e,a,n){"use strict";n.r(a);n("e260"),n("e6cf"),n("cca6"),n("a79d");var t=n("2b0e"),i=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"app"}},[n("LomSection")],1)},s=[],o=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"lom1_section_wrapper"},[n("h2",{staticClass:"title is-clickable",on:{click:e.toggleCollapse}},[e._v(" Leerobject "),n("CollapseIcon",{attrs:{minimized:e.isMinimized}})],1),n("hr"),n("div",{class:{minimized:e.isMinimized},attrs:{id:"lom1_section_block"}},[n("div",{staticClass:"field is-horizontal"},[e._m(0),n("div",{staticClass:"field-body"},[n("TypeSelector")],1)]),n("div",{staticClass:"field is-horizontal"},[e._m(1),n("div",{staticClass:"field-body"},[n("EindgebruikerSelector")],1)]),n("div",{staticClass:"field is-horizontal"},[e._m(2),n("div",{staticClass:"field-body"},[n("TalenSelector")],1)]),n("div",{staticClass:"field is-horizontal"},[e._m(3),n("div",{staticClass:"field-body"},[n("OnderwijsniveausSelector")],1)]),n("div",{staticClass:"field is-horizontal"},[e._m(4),n("div",{staticClass:"field-body"},[n("OnderwijsgradenSelector")],1)]),n("div",{staticClass:"field is-horizontal"},[e._m(5),n("div",{staticClass:"field-body"},[n("ThemaSelector")],1)]),n("div",{staticClass:"field is-horizontal"},[e._m(6),n("div",{staticClass:"field-body"},[n("VakkenSelector")],1)]),n("div",{staticClass:"field is-horizontal"},[e._m(7),n("div",{staticClass:"field-body"},[n("TrefwoordenSelector")],1)])])])},l=[function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label"},[e._v("Type")])])},function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label label-two-lines"},[e._v("Beoogde eindgebruiker")])])},function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label"},[e._v("Taal")])])},function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label"},[e._v("Onderwijsniveaus")])])},function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label"},[e._v("Onderwijsgraden")])])},function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label"},[e._v("Thema")])])},function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label"},[e._v("Vakken")])])},function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"field-label is-normal"},[n("label",{staticClass:"label"},[e._v("Trefwoorden")])])}],r=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"talen_selector"}},[n("multiselect",{attrs:{placeholder:"Kies media type",label:"name","track-by":"code",options:e.options,multiple:!1,taggable:!1,searchable:!1,"show-labels":!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[n("template",{slot:"noResult"},[e._v("Media type niet gevonden")])],2),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"item_type",id:"type_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}}),n("pre",{staticClass:"language-json",attrs:{id:"type_value_preview"}},[n("code",[e._v(e._s(e.value))])])],1)},d=[],c=(n("e9c4"),n("8e5f")),u=n.n(c),m=null,v={name:"TypeSelector",components:{Multiselect:u.a},data:function(){return{value:m,json_value:JSON.stringify(m),options:[{name:"Video",code:"Video"},{name:"Audio",code:"Audio"}]}},created:function(){var e=document.getElementById("item_type");if(e){var a=e.innerText;a&&(m=[{name:a,code:a}],this.json_value=JSON.stringify(m),this.value=m)}},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},h=v,_=(n("60bc"),n("0d67"),n("2877")),g=Object(_["a"])(h,r,d,!1,null,null,null),f=g.exports,p=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"eindgebruikers_selector"}},[n("multiselect",{attrs:{placeholder:"Kies eindgebruikers",label:"name","track-by":"code",options:e.options,multiple:!0,searchable:!1,taggable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[n("template",{slot:"noResult"},[e._v("Beoogde eindgebruiker niet gevonden")])],2),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"lom1_beoogde_eindgebruiker",id:"eindgebruikers_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},k=[],b=[],w={name:"EindgebruikerSelector",components:{Multiselect:u.a},data:function(){return{value:b,json_value:JSON.stringify(b),options:[{name:"Docent",code:"Docent"},{name:"Student",code:"Student"},{name:"Directie",code:"Directie"},{name:"ICT-coördinator",code:"ICT-coördinator"},{name:"Systeembeheerder",code:"Systeembeheerder"},{name:"Preventieadviseur",code:"Preventieadviseur"},{name:"GOK",code:"GOK / Zorgcoördinator"},{name:"Pedagogisch begeleider",code:"Pedagogisch begeleider"},{name:"Inspectielid",code:"Inspectielid"},{name:"Administratief personeel",code:"Administratief personeel"},{name:"Met pensioen",code:"Met pensioen"},{name:"Ouder",code:"Ouder"},{name:"Ander",code:"Ander"}]}},created:function(){var e=document.getElementById("item_eindgebruikers");if(e){var a=JSON.parse(e.innerText);for(var n in a){var t=a[n];b.push({name:t["value"],code:t["value"]})}}this.json_value=JSON.stringify(b)},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},y=w,j=(n("92cc"),Object(_["a"])(y,p,k,!1,null,null,null)),S=j.exports,C=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"talen_selector"}},[n("multiselect",{attrs:{placeholder:"Zoek taal",label:"name","track-by":"code",options:e.options,multiple:!0,taggable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[n("template",{slot:"noResult"},[e._v("Taal niet gevonden")])],2),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"talen",id:"talen_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}}),n("pre",{staticClass:"language-json",attrs:{id:"talen_value_preview"}},[n("code",[e._v(e._s(e.value))])])],1)},O=[],T=(n("b0c0"),[]),N={name:"TalenSelector",components:{Multiselect:u.a},data:function(){return{value:T,json_value:JSON.stringify(T),options:[{name:"Nederlands",code:"nl"},{name:"Frans",code:"fr"},{name:"Duits",code:"de"},{name:"Italiaans",code:"it"},{name:"Engels",code:"en"},{name:"Spaans",code:"es"},{name:"Afar",code:"aa"},{name:"Abchazisch",code:"ab"},{name:"Afrikaans",code:"af"},{name:"Amhaars",code:"am"},{name:"Arabisch",code:"ar"},{name:"Assamees",code:"as"},{name:"Aymara",code:"ay"},{name:"Azerbeidzjaans",code:"az"},{name:"Basjkir",code:"ba"},{name:"Wit-Russisch",code:"be"},{name:"Bislama",code:"bi"},{name:"Bengaals",code:"bn"},{name:"Tibetaans",code:"bo"},{name:"Bretons",code:"br"},{name:"Catalaans",code:"ca"},{name:"Tsjechisch",code:"cs"},{name:"Welch",code:"cy"},{name:"Deens",code:"da"},{name:"Bhutani",code:"dz"},{name:"Grieks",code:"el"},{name:"Esperanto",code:"eo"},{name:"Ests",code:"et"},{name:"Baskisch",code:"eu"},{name:"Perzisch",code:"fa"},{name:"Fins",code:"fi"},{name:"Fiji",code:"fj"},{name:"Iers",code:"ga"},{name:"Schots Gaelic",code:"gd"},{name:"Galicisch",code:"gl"},{name:"Guarani",code:"gn"},{name:"Gujarati",code:"gu"},{name:"Hausa",code:"ha"},{name:"Hebreeuws",code:"he"},{name:"Hindi",code:"hi"},{name:"Hongaars",code:"hu"},{name:"Kroatisch",code:"hr"},{name:"Hongaars",code:"hu"},{name:"Armeens",code:"hy"},{name:"Interlingua",code:"ia"},{name:"Indonesisch",code:"id"},{name:"Interlingue",code:"ie"},{name:"Inupiak",code:"ik"},{name:"IJslands",code:"is"},{name:"Inuktitut (Eskimo)",code:"iu"},{name:"Japans",code:"ja"},{name:"Georgisch",code:"ka"},{name:"Kazachs",code:"kk"},{name:"Groenlands",code:"kl"},{name:"Cambodjaans",code:"km"},{name:"Kannada",code:"kn"},{name:"Koreaans",code:"ko"},{name:"Kasjmir",code:"ks"},{name:"Koerdisch",code:"ku"},{name:"Kirgizisch",code:"ky"},{name:"latijns",code:"la"},{name:"Lingala",code:"ln"},{name:"Laotiaans",code:"lo"},{name:"Litouws",code:"lt"},{name:"Lets, Lets",code:"lv"},{name:"Malagasi",code:"mg"},{name:"Macedonisch",code:"mk"},{name:"Malayalam",code:"ml"},{name:"Mongools",code:"mn"},{name:"Marathi",code:"mr"},{name:"Maleis",code:"ms"},{name:"Maltees",code:"mt"},{name:"Birmaans",code:"my"},{name:"Nauru",code:"na"},{name:"Nepalees",code:"ne"},{name:"Noors",code:"no"},{name:"Occitaans",code:"oc"},{name:"(Afan) Oromo",code:"om"},{name:"Oriya",code:"or"},{name:"Punjabi",code:"pa"},{name:"Pools",code:"pl"},{name:"Pashto, Pushto",code:"ps"},{name:"Portugees",code:"pt"},{name:"Quechua",code:"qu"},{name:"Reto-Romaans",code:"rm"},{name:"Kirundi",code:"rn"},{name:"Roemeens",code:"ro"},{name:"Russisch",code:"ru"},{name:"Kinyarwanda",code:"rw"},{name:"Sanskriet",code:"sa"},{name:"Sindhi",code:"sd"},{name:"Sangro",code:"sg"},{name:"Servo-Kroatisch",code:"sh"},{name:"Singalees",code:"si"},{name:"Slowaaks",code:"sk"},{name:"Sloveens",code:"sl"},{name:"Samoaans",code:"sm"},{name:"Shona",code:"sn"},{name:"Somalisch",code:"so"},{name:"Albanees",code:"sq"},{name:"Servisch",code:"sr"},{name:"Siswati",code:"ss"},{name:"Sesotho",code:"st"},{name:"Soedanees",code:"su"},{name:"Zweeds",code:"sv"},{name:"Swahili",code:"sw"},{name:"Tamil",code:"ta"},{name:"Telugu",code:"te"},{name:"Tadzjieks",code:"tg"},{name:"Thais",code:"th"},{name:"Tigrinya",code:"ti"},{name:"Turkmeens",code:"tk"},{name:"Tagalog",code:"tl"},{name:"Setswana",code:"tn"},{name:"Tonga",code:"to"},{name:"Turks",code:"tr"},{name:"Tsonga",code:"ts"},{name:"Tataars",code:"tt"},{name:"twee keer",code:"tw"},{name:"Oeigoers",code:"ug"},{name:"Oekraïens",code:"uk"},{name:"Urdu",code:"ur"},{name:"Oezbeeks",code:"uz"},{name:"Vietnamees",code:"vi"},{name:"Volapuk",code:"vo"},{name:"Wolof",code:"wo"},{name:"Xhosa",code:"xh"},{name:"Jiddisch",code:"yi"},{name:"Yoruba",code:"yo"},{name:"Zhuang",code:"za"},{name:"Chinees",code:"zh"},{name:"Zulu",code:"zu"}]}},created:function(){var e=document.getElementById("item_languages");if(e){var a=JSON.parse(e.innerText);for(var n in a){var t=a[n]["value"],i="todo";for(var s in this.options){var o=this.options[s];if(o["code"]==t){i=o["name"];break}}T.push({name:i,code:t})}}this.json_value=JSON.stringify(T)},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},E=N,x=(n("b486"),Object(_["a"])(E,C,O,!1,null,null,null)),I=x.exports,V=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"onderwijsniveaus_selector"}},[n("multiselect",{attrs:{placeholder:"Selecteer onderwijsniveaus",label:"label","track-by":"id",options:e.options,multiple:!0,searchable:!1,taggable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[n("template",{slot:"noResult"},[e._v("Onderwijsniveau niet gevonden")])],2),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"lom1_beoogde_eindgebruiker",id:"onderwijsniveaus_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},J=[],z=n("bc3a"),A=n.n(z),M=[],R={name:"OnderwijsniveausSelector",components:{Multiselect:u.a},data:function(){return{value:M,json_value:JSON.stringify(M),options:[{id:"",label:"Onderwijsniveaus inladen...",definition:"Onderwijsniveaus inladen..."}]}},created:function(){var e=this,a="http://localhost:5000",n=document.getElementById("redactie_api_url");n&&(a=n.innerText,A.a.get(a+"/onderwijsniveaus").then((function(a){e.options=a.data;var n=document.getElementById("item_onderwijsniveaus");if(n){var t=JSON.parse(n.innerText),i={},s={};if(t["show_legacy"]){console.log("legacy fallback voor onderwijsniveaus (lom_context)...");var o=document.getElementById("item_onderwijsniveaus_legacy");if(o){var l=JSON.parse(o.innerText);for(var r in l)for(var d in i["definition"]=l[r]["value"],e.options)if(s=e.options[d],i["definition"]==s["definition"]){i["id"]=s["id"],i["label"]=s["label"],M.push({id:i["id"],label:i["label"],definition:i["definition"]});break}}}else for(var c in console.log("loading new onderwijsniveaus from (lom_onderwijsniveau)..."),t)for(var u in i["id"]=t[c]["value"],e.options)if(s=e.options[u],i["id"]==s["id"]){i["label"]=s["label"],i["definition"]=s["definition"],M.push({id:i["id"],label:i["label"],definition:i["definition"]});break}}})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},B=R,P=(n("a304"),Object(_["a"])(B,V,J,!1,null,null,null)),$=P.exports,G=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"onderwijsgraden_selector"}},[n("multiselect",{attrs:{placeholder:"Selecteer onderwijsgraden",label:"label","track-by":"id",options:e.options,multiple:!0,taggable:!1,searchable:!1},on:{input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[n("template",{slot:"noResult"},[e._v("Onderwijsgraad niet gevonden")])],2),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"lom1_onderwijsgraden",id:"onderwijsgraden_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},L=[],K=[],H={name:"OnderwijsgradenSelector",components:{Multiselect:u.a},data:function(){return{value:K,json_value:JSON.stringify(K),options:[{id:"loading...",label:"Onderwijsgraden inladen...",definition:"Onderwijsgraden inladen..."}]}},created:function(){var e=this,a="http://localhost:5000",n=document.getElementById("redactie_api_url");n&&(a=n.innerText,A.a.get(a+"/onderwijsgraden").then((function(a){e.options=a.data;var n=document.getElementById("item_onderwijsgraden");if(n){var t=JSON.parse(n.innerText),i={};if(n&&t["show_legacy"]){console.log("legacy fallback voor onderwijsgraden (lom_typicalagerange)...");var s=document.getElementById("item_onderwijsgraden_legacy");if(s){var o=JSON.parse(s.innerText),l={};for(var r in o){var d=o[r]["value"];for(var c in l["definition"]=d,e.options)if(i=e.options[c],l["definition"]==i["definition"]){l["id"]=i["id"],l["label"]=i["label"],K.push({id:l["id"],label:l["label"],definition:l["definition"]});break}}}}else for(var u in console.log("loading new onderwijsgraden from (lom_onderwijsgraad)..."),t)for(var m in l["id"]=t[u]["value"],e.options)if(i=e.options[m],l["id"]==i["id"]){l["label"]=i["label"],l["definition"]=i["definition"],K.push({id:l["id"],label:l["label"],definition:l["definition"]});break}e.$root.$emit("graden_changed",K)}})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e),this.$root.$emit("graden_changed",e)}}},D=H,F=(n("f329"),Object(_["a"])(D,G,L,!1,null,null,null)),Z=F.exports,W=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"thema_selector"}},[n("multiselect",{attrs:{"tag-placeholder":"Voeg nieuw thema toe",placeholder:"Zoek thema",label:"label","track-by":"id",options:e.options,"option-height":104,"show-labels":!1,multiple:!0,taggable:!1},on:{input:e.updateValue},scopedSlots:e._u([{key:"singleLabel",fn:function(a){return[n("span",{staticClass:"option__desc"},[n("span",{staticClass:"option__title"},[e._v(" "+e._s(a.option.label)+" ")]),n("span",{staticClass:"option_small"},[e._v(" "+e._s(a.option.definition)+" ")])])]}},{key:"option",fn:function(a){return[n("div",{staticClass:"option__desc"},[n("span",{staticClass:"option__title"},[e._v(e._s(a.option.label))]),n("span",{staticClass:"option__small"},[e._v(e._s(a.option.definition))])])]}}]),model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[n("template",{slot:"noResult"},[e._v("Thema niet gevonden")])],2),n("a",{staticClass:"button is-link is-small toon-themas-button",on:{click:e.toggleThemas}},[e._v(" "+e._s(e.show_themas_label)+" ")]),n("div",{staticClass:"thema-search",class:[e.show_thema_cards?"show":"hide"]},[n("div",{staticClass:"field has-addons"},[n("div",{staticClass:"control"},[n("input",{directives:[{name:"model",rawName:"v-model",value:e.thema_search,expression:"thema_search"}],staticClass:"input is-small",attrs:{type:"text",placeholder:"Zoek thema"},domProps:{value:e.thema_search},on:{keydown:function(a){return!a.type.indexOf("key")&&e._k(a.keyCode,"enter",13,a.key,"Enter")?null:e.zoekThemas(a)},input:function(a){a.target.composing||(e.thema_search=a.target.value)}}})]),n("div",{staticClass:"control"},[n("a",{staticClass:"button is-info is-small",on:{click:function(a){return e.zoekThemas(a)}}},[e._v(" Zoek ")])])])]),n("div",{staticClass:"thema-warning-pill",class:[e.show_already_added_warning?"show":"hide"]},[e._v(" Thema werd al toegevoegd ")]),n("div",{staticClass:"thema-cards",class:[e.show_thema_cards?"show":"hide"]},[e.thema_cards.length?e._e():n("div",{staticClass:"notification is-info is-light"},[e._v(' Geen themas gevonden met de zoekterm "'+e._s(e.thema_prev_search)+'". ')]),e._l(e.thema_cards,(function(a,t){return n("div",{key:t,staticClass:"columns"},e._l(a,(function(a){return n("div",{key:a.id,staticClass:"column is-one-quarter"},[n("div",{staticClass:"tile is-ancestor"},[n("div",{staticClass:"tile is-vertical mr-2 mt-2"},[n("div",{staticClass:"card",class:[e.themaIsSelected(a)?"thema-selected":""],on:{click:function(n){return e.toggleThemaSelect(a)}}},[n("header",{staticClass:"card-header"},[n("p",{staticClass:"card-header-title"},[e._v(" "+e._s(a.label)+" ")])]),n("div",{staticClass:"card-content"},[e._v(" "+e._s(a.definition)+" ")])])])])])})),0)}))],2),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"themas",id:"thema_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},q=[],U=(n("caad"),n("2532"),n("a434"),[]),Q={name:"ThemaSelector",components:{Multiselect:u.a},data:function(){return{value:U,json_value:JSON.stringify(U),options:[{id:"",label:"Themas inladen...",definition:"Themas inladen..."}],thema_cards:[],show_thema_cards:!1,show_already_added_warning:!1,show_themas_label:"Toon themas",thema_search:"",thema_prev_search:""}},created:function(){var e=this,a="http://localhost:5000",n=document.getElementById("redactie_api_url");n&&(a=n.innerText,A.a.get(a+"/themas").then((function(a){for(var n in e.options=[],a.data){var t=a.data[n];t.label.length>1&&e.options.push(t)}})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e),this.$root.$emit("themas_changed",e)},zoekThemas:function(e){this.thema_cards=[];var a=[];for(var n in this.options){var t=this.options[n],i=this.thema_search.toLowerCase(),s=t.label.toLowerCase(),o=t.definition.toLowerCase();(s.includes(i)||o.includes(i))&&a.push(Object.assign({},t)),4==a.length&&(this.thema_cards.push(JSON.parse(JSON.stringify(a))),a=[])}a.length>0&&this.thema_cards.push(JSON.parse(JSON.stringify(a))),this.thema_prev_search=this.thema_search,this.thema_search="",e.preventDefault()},themaIsSelected:function(e){for(var a in this.value){var n=this.value[a];if(e.id==n.id)return!0}return!1},toggleThemas:function(){this.show_thema_cards=!this.show_thema_cards,this.show_thema_cards?this.show_themas_label="Verberg themas":(this.show_themas_label="Toon themas",this.thema_cards=[]),this.thema_cards=[];var e=[];for(var a in this.options)e.push(this.options[a]),4==e.length&&(this.thema_cards.push(e),e=[]);e.length>0&&this.thema_cards.push(e)},toggleThemaSelect:function(e){var a=!1;for(var n in this.value){var t=this.value[n];if(t.id==e.id){a=!0,this.value.splice(n,1),this.json_value=JSON.stringify(this.value);break}}if(!a){var i={id:e.id,label:e.label,definition:e.definition};this.value.push(i),this.json_value=JSON.stringify(this.value)}}}},X=Q,Y=(n("7b46"),Object(_["a"])(X,W,q,!1,null,null,null)),ee=Y.exports,ae=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"vakken_selector"}},[n("multiselect",{attrs:{id:"vakken_multiselect","tag-placeholder":"Kies vakken",placeholder:"Zoek vak",label:"label","track-by":"id",options:e.options,multiple:!0,taggable:!1},on:{input:e.updateValue},scopedSlots:e._u([{key:"singleLabel",fn:function(a){return[n("span",{staticClass:"option__desc"},[n("span",{staticClass:"option__title"},[e._v(" "+e._s(a.option.label)+" ")]),n("span",{staticClass:"option_small"},[e._v(" "+e._s(a.option.definition)+" ")])])]}},{key:"option",fn:function(a){return[n("div",{staticClass:"option__desc"},[n("span",{staticClass:"option__title"},[e._v(e._s(a.option.label))]),n("span",{staticClass:"option__small"},[e._v(e._s(a.option.definition))])])]}}]),model:{value:e.value,callback:function(a){e.value=a},expression:"value"}},[n("template",{slot:"noResult"},[e._v("Vak niet gevonden")])],2),n("a",{staticClass:"button is-link is-small vakken-suggest-button",on:{click:e.toggleSuggesties}},[e._v(" "+e._s(e.suggestie_btn_label)+" ")]),n("div",{staticClass:"vak-warning-pill",class:[e.show_already_added_warning?"show":"hide"]},[e._v(" Vak werd al toegevoegd ")]),n("div",{staticClass:"vakken-suggesties",class:[e.show_vakken_suggesties?"show":"hide"]},[n("h3",{staticClass:"subtitle vakken-title"},[e._v("Suggesties voor vakken")]),e.vakken_suggesties.length?e._e():n("div",{staticClass:"notification is-info is-light"},[e._v(" Geen suggesties gevonden. Probeer andere themas of onderwijsgraden te selecteren. ")]),e._l(e.vakken_suggesties,(function(a,t){return n("div",{key:"vak"+t,staticClass:"columns"},e._l(a,(function(a){return n("div",{key:a.id,staticClass:"column is-one-quarter"},[n("div",{staticClass:"tile is-ancestor"},[n("div",{staticClass:"tile is-vertical mr-2 mt-2"},[n("div",{staticClass:"card",class:[e.vakIsSelected(a)?"vak-selected":""],on:{click:function(n){return e.toggleVakSelect(a)}}},[n("header",{staticClass:"card-header"},[n("p",{staticClass:"card-header-title"},[e._v(" "+e._s(a.label)+" ")])]),n("div",{staticClass:"card-content"},[e._v(" "+e._s(a.definition)+" ")])])])])])})),0)})),n("h3",{staticClass:"subtitle vakken-title"},[e._v("Overige vakken")]),e._l(e.overige_vakken,(function(a,t){return n("div",{key:"sug"+t,staticClass:"columns"},e._l(a,(function(a){return n("div",{key:a.id,staticClass:"column is-one-quarter"},[n("div",{staticClass:"tile is-ancestor"},[n("div",{staticClass:"tile is-vertical mr-2 mt-2"},[n("div",{staticClass:"card",class:[e.vakIsSelected(a)?"vak-selected":""],on:{click:function(n){return e.toggleVakSelect(a)}}},[n("header",{staticClass:"card-header"},[n("p",{staticClass:"card-header-title"},[e._v(" "+e._s(a.label)+" ")])]),n("div",{staticClass:"card-content"},[e._v(" "+e._s(a.definition)+" ")])])])])])})),0)}))],2),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"vakken",id:"vakken_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}})],1)},ne=[],te=[],ie={name:"VakkenSelector",components:{Multiselect:u.a},props:{},data:function(){return{value:te,json_value:JSON.stringify(te),options:[{id:"1",label:"Vakken inladen...",definition:"Vakken inladen..."}],show_vakken_suggesties:!1,show_already_added_warning:!1,suggestie_btn_label:"Toon suggesties voor vakken",vakken_suggesties:[],overige_vakken:[],graden:[],themas:[]}},mounted:function(){var e=this;this.$root.$on("graden_changed",(function(a){console.log("graden changed data=",a),e.graden=a,e.updateSuggestions()})),this.$root.$on("themas_changed",(function(a){console.log("themas changed data=",a),e.themas=a,e.updateSuggestions()}))},created:function(){var e=this,a="http://localhost:5000",n=document.getElementById("redactie_api_url");n&&(a=n.innerText,A.a.get(a+"/vakken").then((function(a){e.options=a.data})))},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)},vakIsSelected:function(e){for(var a in this.value){var n=this.value[a];if(e.id==n.id)return!0}return!1},updateOverigeVakken:function(e,a){var n=this;A.a.get(e+"/vakken").then((function(e){n.overige_vakken=[];var t=[];for(var i in e.data){var s=e.data[i];void 0==a[s.id]&&t.push(Object.assign({},s)),t.length>=4&&(n.overige_vakken.push(t),t=[])}t.length>0&&n.overige_vakken.push(t)}))},updateSuggestions:function(){var e=this,a="http://localhost:5000",n=document.getElementById("redactie_api_url");if(n)if(a=n.innerText,this.show_vakken_suggesties){var t={graden:this.graden,themas:this.themas};if(0==t["graden"].length||0==t["themas"].length)return this.vakken_suggesties=[],void this.updateOverigeVakken(a,{});A.a.post(a+"/vakken_suggest",t).then((function(n){e.vakken_suggesties=[];var t=[],i={};for(var s in n.data){var o=n.data[s];i[o.id]=o,t.push(Object.assign({},o)),4==t.length&&(e.vakken_suggesties.push(t),t=[])}t.length>0&&e.vakken_suggesties.push(t),console.log("suggest_map=",i),e.updateOverigeVakken(a,i)}))}else console.log("Vakken suggestions is closed, not loading...")},toggleSuggesties:function(){this.show_vakken_suggesties=!this.show_vakken_suggesties,this.show_vakken_suggesties?(this.suggestie_btn_label="Verberg suggesties voor vakken",console.log("make axios call here...")):this.suggestie_btn_label="Toon suggesties voor vakken",this.updateSuggestions()},toggleVakSelect:function(e){var a=!1;for(var n in this.value){var t=this.value[n];if(t.id==e.id){a=!0,this.value.splice(n,1),this.json_value=JSON.stringify(this.value);break}}if(!a){var i={id:e.id,label:e.label,definition:e.definition};this.value.push(i),this.json_value=JSON.stringify(this.value)}}}},se=ie,oe=(n("569e"),Object(_["a"])(se,ae,ne,!1,null,null,null)),le=oe.exports,re=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{attrs:{id:"trefwoorden_selector"}},[n("multiselect",{attrs:{"tag-placeholder":"Maak nieuw trefwoord aan",placeholder:"Zoek of voeg een nieuw trefwoord toe",label:"name","track-by":"code",options:e.options,multiple:!0,taggable:!0},on:{tag:e.addTrefwoord,input:e.updateValue},model:{value:e.value,callback:function(a){e.value=a},expression:"value"}}),n("textarea",{directives:[{name:"model",rawName:"v-model",value:e.json_value,expression:"json_value"}],attrs:{name:"trefwoorden",id:"trefwoorden_json_value"},domProps:{value:e.json_value},on:{input:function(a){a.target.composing||(e.json_value=a.target.value)}}}),n("div",{staticClass:"cp_keywords_button"},[n("a",{on:{click:e.toggleKeywordCollapse}},[e._v(" "+e._s(e.cp_keyword_label)+" ")]),n("div",{staticClass:"warning-pill",class:[e.show_already_added_warning?"show":"hide"]},[e._v(" Keyword werd al toegevoegd ")])]),n("div",{staticClass:"cp_keywords",class:[e.show_cp_keywords?"show":"hide"]},[e.cp_keywords.length?e._e():n("div",{staticClass:"notification is-info is-light"},[e._v(" Voor dit item zijn er geen Content Partner trefwoorden. ")]),e._l(e.cp_keywords,(function(a){return n("div",{key:a.code,staticClass:"keyword-pill",on:{click:function(n){return e.addCpKeyword(a)}}},[e._v(" "+e._s(a.name)+" ")])}))],2)],1)},de=[],ce=[],ue={name:"TrefwoordenSelector",components:{Multiselect:u.a},props:{},data:function(){return{value:ce,json_value:JSON.stringify(ce),options:[{name:"reportage",code:"reportage"},{name:"Silent Movie",code:"Silent Movie"},{name:"Belgium",code:"Belgium"},{name:"France",code:"France"},{name:"Spain",code:"Spain"},{name:"BURGER",code:"BURGER"},{name:"CONFLICT",code:"CONFLICT"},{name:"CONVENTIE VAN GENEVE",code:"CONVENTIE VAN GENEVE"},{name:"INTERNATIONAAL STRAFGERECHTSHOF",code:"INTERNATIONAAL STRAFGERECHTSHOF"},{name:"MENSENRECHT",code:"MENSENRECHT"},{name:"OORLOG",code:"OORLOG"},{name:"OORLOGSMISDAAD",code:"OORLOGSMISDAAD"},{name:"SCHENDING",code:"SCHENDING"},{name:"STRAFRECHT",code:"STRAFRECHT"},{name:"VAN DEN WIJNGAERT CHRIS",code:"VAN DEN WIJNGAERT CHRIS"},{name:"VEILIGHEID",code:"VEILIGHEID"},{name:"Christiane van den Wijngaert",code:"Christiane van den Wijngaert"},{name:"conventie van Genève",code:"conventie van Genève"},{name:"Internationaal Strafhof",code:"Internationaal Strafhof"},{name:"justitie",code:"justitie"},{name:"mensenrechten",code:"mensenrechten"},{name:"oorlog",code:"oorlog"}],cp_keywords:[],show_cp_keywords:!1,show_already_added_warning:!1,cp_keyword_label:"Bekijk trefwoorden van Content Partners"}},created:function(){var e=document.getElementById("item_keywords");if(e){var a=JSON.parse(e.innerText);for(var n in a){var t=a[n];ce.push({name:t["value"],code:t["value"]})}this.json_value=JSON.stringify(ce)}var i=document.getElementById("item_keywords_cp");if(i){var s=JSON.parse(i.innerText);for(var o in s){var l=s[o];this.cp_keywords.push({name:l["value"],code:l["value"]})}}},methods:{addTrefwoord:function(e){console.log("addTrefwoord nieuw woord=",e);var a={name:e,code:e.substring(0,2)+Math.floor(1e7*Math.random())};this.options.push(a),this.value.push(a),this.json_value=JSON.stringify(this.value)},updateValue:function(e){this.json_value=JSON.stringify(e)},toggleKeywordCollapse:function(){this.show_cp_keywords=!this.show_cp_keywords,this.show_cp_keywords?this.cp_keyword_label="Verberg trefwoorden van Content Partners":this.cp_keyword_label="Bekijk trefwoorden van Content Partners"},addCpKeyword:function(e){var a=this,n=!1;for(var t in this.value){var i=this.value[t];if(i.code==e.code){n=!0;break}}if(n)this.show_already_added_warning=!0,setTimeout((function(){a.show_already_added_warning=!1}),3e3);else{var s={name:e.name,code:e.code};this.options.push(s),this.value.push(s),this.json_value=JSON.stringify(this.value)}}}},me=ue,ve=(n("ea01"),Object(_["a"])(me,re,de,!1,null,null,null)),he=ve.exports,_e=function(){var e=this,a=e.$createElement,n=e._self._c||a;return n("div",{staticClass:"minimize-icon-wrapper"},[n("span",{class:[e.minimized?"icon-folded":"icon-unfolded"]},[n("ion-icon",{staticClass:"md hydrated",attrs:{name:"chevron-down-circle-outline",role:"img","aria-label":"chevron down circle outline"}})],1),n("span",{class:[e.minimized?"icon-unfolded":"icon-folded"]},[n("ion-icon",{staticClass:"md hydrated",attrs:{name:"chevron-forward-circle-outline",role:"img","aria-label":"chevron forward circle outline"}})],1)])},ge=[],fe={name:"CollapseIcon",components:{},props:{minimized:Boolean},methods:{updateValue:function(e){this.json_value=JSON.stringify(e)}}},pe=fe,ke=(n("c6f0"),Object(_["a"])(pe,_e,ge,!1,null,null,null)),be=ke.exports,we=document.getElementById("pid");if(we){var ye=we.innerText;console.log("LomSection for pid=",ye)}var je={name:"LomSection",components:{TypeSelector:f,EindgebruikerSelector:S,TalenSelector:I,OnderwijsniveausSelector:$,OnderwijsgradenSelector:Z,ThemaSelector:ee,VakkenSelector:le,TrefwoordenSelector:he,CollapseIcon:be},data:function(){return{isMinimized:!1,pid:ye}},methods:{toggleCollapse:function(){this.isMinimized=!this.isMinimized}}},Se=je,Ce=(n("080a"),Object(_["a"])(Se,o,l,!1,null,null,null)),Oe=Ce.exports,Te={name:"App",components:{LomSection:Oe}},Ne=Te,Ee=(n("034f"),Object(_["a"])(Ne,i,s,!1,null,null,null)),xe=Ee.exports;t["a"].config.productionTip=!1,t["a"].config.ignoredElements=[/^ion-/],new t["a"]({render:function(e){return e(xe)}}).$mount("#app")},6586:function(e,a,n){},"68f1":function(e,a,n){},"71d9":function(e,a,n){},"7b46":function(e,a,n){"use strict";n("68f1")},"85ec":function(e,a,n){},"85ef":function(e,a,n){},"90d9":function(e,a,n){},"92cc":function(e,a,n){"use strict";n("b2c9")},"97c9":function(e,a,n){},a304:function(e,a,n){"use strict";n("71d9")},a612:function(e,a,n){},b2c9:function(e,a,n){},b486:function(e,a,n){"use strict";n("97c9")},c6f0:function(e,a,n){"use strict";n("6586")},e2fe:function(e,a,n){},ea01:function(e,a,n){"use strict";n("90d9")},f329:function(e,a,n){"use strict";n("14dd")}});
//# sourceMappingURL=app.247c826c.js.map