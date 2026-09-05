/* ==================================================================
 * sim_balance_energetico.js
 * ¿A dónde va la energía de una ruptura finita? Simulación SVG que
 * sintetiza el sismograma en tres receptores y muestra el balance E0.
 *
 *   ADELANTE (Este)  -> pulso CORTO y ALTO   (forward directivity)
 *   LADO (Norte)     -> intermedio           (atenuación normal)
 *   ATRÁS (Oeste)    -> tren LARGO y BAJO     (backward directivity)
 * Los tres reciben ~la misma ENERGÍA total (área), pero con PGA muy
 * distinto: la directividad redistribuye, no crea ni destruye energía.
 *
 * Balance:  E0 = Es (radiada, "pétalos", 10-30%) + EG (fractura) + ED (fricción/calor).
 * Solo Es forma las ondas; se reparte según la directividad de arriba.
 *
 * ONDAS: el pulso grande y directivo es la ONDA S (roja, lenta, la dominante).
 * La ONDA P (azul) es más rápida (Vp = Vs·1,73) -> llega ANTES, y más pequeña.
 * Se dibujan ambas (frentes en el mapa y pulsos en los sismogramas) y se rotulan.
 *
 * POLARIZACIÓN S: en cada receptor una doble flecha TRANSVERSAL AL RAYO (la
 * dirección de cizalla), que ROTA con el azimut: N–S en adelante/atrás (Este/
 * Oeste, sobre el eje), E–O en el lado (Norte). El marcador oscila en esa
 * dirección al pasar la S. (La N–S del eje coincide con "⊥ a la falla" solo
 * porque ahí el rayo va a lo largo de la falla; fuera del eje, rota.)
 *
 * Sin dependencias (CSP-safe, embebible).
 *   var s = SimBalanceEnergetico.crear(div, {beta:0.8, esRad:0.2});
 *   s.setParam('beta',1.2); s.pause(); s.play(); s.reset();
 * ================================================================== */
(function (global) {
  "use strict";
  var SVGNS = "http://www.w3.org/2000/svg";
  function el(t, a){ var e=document.createElementNS(SVGNS,t); if(a)for(var k in a)e.setAttribute(k,a[k]); return e; }
  function hEl(t, c, x){ var e=document.createElement(t); if(c)e.className=c; if(x!=null)e.textContent=x; return e; }

  var DEF = {
    beta: 0.8,       // Vr/c
    L: 240,          // longitud de falla (u. mapa)
    lambda: 30,      // longitud de onda
    nSources: 20,    // subfuentes (Huygens)
    c: 120,          // velocidad de onda (u/seg sim)
    speed: 1.0,      // velocidad de animación
    esRad: 0.20      // fracción de energía radiada Es/E0 (0.10-0.30)
  };

  // mapa 0..460 x 0..320 ; falla centrada, nucleación izquierda
  var MW=460, MH=320, MCY=160, MCX=230, RD=150; // RD: distancia receptores
  var NS=500; // muestras del sismograma
  var VPVS=1.73;      // Vp/Vs  (la P viaja 1,73× más rápido que la S)
  var APREL=0.22;     // amplitud de la P relativa al pico S (P lleva menos energía)

  var CSS_ID="sim-be-css";
  function css(){
    if(document.getElementById(CSS_ID))return;
    var s=document.createElement("style"); s.id=CSS_ID;
    s.textContent=[
      ".simbe{--bg:#f7f9fc;--card:#fff;--ink:#1a2634;--muted:#5b6b7d;--edge:#d5dde6;",
      "  --wave:#8fb8dc;--waveP:#2d6ebe;--waveS:#e4572e;",
      "  --fault:#e4572e;--fwd:#e4572e;--lat:#e9b949;--bwd:#2a9d8f;",
      "  --es:#e4572e;--eg:#e9b949;--ed:#6b7c8f;",
      "  font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);}",
      /* Paleta oscura: se declara dos veces, igual que en la página madre —
         por preferencia del sistema (salvo data-theme="light" explícito) y
         por data-theme="dark", que es lo que fija el botón de tema del blog.
         Con sólo la media query el inserto se quedaba claro dentro de una
         página en modo oscuro. */
      "@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]) .simbe{",
      "  --bg:#0f1720;--card:#16212e;--ink:#e7edf3;",
      "  --muted:#9fb0c0;--edge:#2a3a4b;--wave:#3b5b74;--waveP:#5fa0e6;--waveS:#ff7a54;",
      "  --fault:#ff7a54;--fwd:#ff7a54;--lat:#f2c94c;--bwd:#3fc9b5;",
      "  --es:#ff7a54;--eg:#f2c94c;--ed:#8394a5;}}",
      ":root[data-theme=\"dark\"] .simbe{--bg:#0f1720;--card:#16212e;--ink:#e7edf3;",
      "  --muted:#9fb0c0;--edge:#2a3a4b;--wave:#3b5b74;--waveP:#5fa0e6;--waveS:#ff7a54;",
      "  --fault:#ff7a54;--fwd:#ff7a54;--lat:#f2c94c;--bwd:#3fc9b5;",
      "  --es:#ff7a54;--eg:#f2c94c;--ed:#8394a5;}",
      ".simbe .fig{display:flex;flex-wrap:wrap;gap:12px;}",
      ".simbe .map{flex:1 1 300px;min-width:280px;background:var(--card);",
      "  border:1px solid var(--edge);border-radius:10px;padding:8px;}",
      ".simbe .traces{flex:1 1 320px;min-width:280px;display:flex;flex-direction:column;gap:8px;}",
      ".simbe .tr{background:var(--card);border:1px solid var(--edge);border-radius:10px;padding:6px 8px;}",
      ".simbe .tr .hd{display:flex;justify-content:space-between;font-size:12px;font-weight:700;}",
      ".simbe .tr .hd .r{font-weight:500;color:var(--muted);}",
      ".simbe svg{width:100%;height:auto;display:block;}",
      ".simbe .bud{margin-top:10px;background:var(--card);border:1px solid var(--edge);",
      "  border-radius:10px;padding:8px 10px;}",
      ".simbe .bud .lbl{font-size:12px;font-weight:700;margin-bottom:4px;}",
      ".simbe .note{font-size:11.5px;color:var(--muted);margin-top:6px;line-height:1.5;}"
    ].join("");
    document.head.appendChild(s);
  }

  function crear(container, opciones){
    css();
    var P={}; for(var k in DEF)P[k]=DEF[k];
    if(opciones)for(var k2 in opciones)P[k2]=opciones[k2];

    container.classList.add("simbe"); container.innerHTML="";
    var fig=hEl("div","fig");

    // ---- panel mapa ----
    var mapWrap=hEl("div","map");
    mapWrap.appendChild(hEl("div","note","Falla rompiendo hacia el Este (→). Receptores a igual distancia."));
    var map=el("svg",{viewBox:"0 0 "+MW+" "+MH,preserveAspectRatio:"xMidYMid meet"});
    mapWrap.appendChild(map);
    var gW=el("g",{}); map.appendChild(gW); var wpool=[];
    var gT=el("g",{}); map.appendChild(gT);
    fig.appendChild(mapWrap);

    // ---- columna de trazas ----
    var col=hEl("div","traces");
    var recs=[
      {key:"fwd",nom:"ADELANTE (Este · La Guaira)",col:"var(--fwd)",x:MCX+RD,y:MCY,theta:0},
      {key:"lat",nom:"LADO (Norte · mar)",        col:"var(--lat)",x:MCX,   y:MCY-RD,theta:Math.PI/2},
      {key:"bwd",nom:"ATRÁS (Oeste)",             col:"var(--bwd)",x:MCX-RD,y:MCY,theta:Math.PI}
    ];
    recs.forEach(function(r){
      var box=hEl("div","tr");
      var hd=hEl("div","hd"); hd.appendChild(hEl("span",null,r.nom));
      r.readEl=hEl("span","r",""); hd.appendChild(r.readEl); box.appendChild(hd);
      var sv=el("svg",{viewBox:"0 0 320 78",preserveAspectRatio:"none"});
      sv.appendChild(el("line",{x1:0,y1:70,x2:320,y2:70,stroke:"var(--edge)","stroke-width":1}));
      r.gInd=el("g",{}); sv.appendChild(r.gInd); r.indPool=[];   // aporte de cada punto de falla
      r.gTk =el("g",{}); sv.appendChild(r.gTk);  r.tkPool=[];    // marca de arribo por punto
      r.pFull=el("polyline",{fill:"none",stroke:"var(--waveP)","stroke-opacity":0.30,"stroke-width":1.1});
      r.pLive=el("polyline",{fill:"none",stroke:"var(--waveP)","stroke-width":1.7});
      r.full=el("polyline",{fill:"none",stroke:r.col,"stroke-opacity":0.30,"stroke-width":1.2});
      r.live=el("polyline",{fill:"none",stroke:r.col,"stroke-width":1.9});
      r.cur =el("circle",{r:3,fill:r.col});
      r.lblP=el("text",{"font-size":9,"font-weight":"700",fill:"var(--waveP)","text-anchor":"middle"}); r.lblP.textContent="P";
      r.lblS=el("text",{"font-size":9,"font-weight":"700",fill:r.col,"text-anchor":"middle"}); r.lblS.textContent="S";
      sv.appendChild(r.pFull); sv.appendChild(r.pLive);
      sv.appendChild(r.full); sv.appendChild(r.live); sv.appendChild(r.cur);
      sv.appendChild(r.lblP); sv.appendChild(r.lblS);
      box.appendChild(sv); col.appendChild(box);

      // --- POLARIZACIÓN de la S: doble flecha TRANSVERSAL AL RAYO (cizalla).
      //     Perpendicular a la propagación hacia ESE receptor -> rota con el
      //     azimut: N–S en adelante/atrás (Este/Oeste), E–O en el lado (Norte). ---
      var dx=r.x-MCX, dy=r.y-MCY, rn=Math.hypot(dx,dy)||1;
      r.tux=-dy/rn; r.tuy=dx/rn;                 // vector transversal (⊥ al rayo)
      var AL=22, hp=6;
      var ax1=r.x-AL*r.tux, ay1=r.y-AL*r.tuy, ax2=r.x+AL*r.tux, ay2=r.y+AL*r.tuy;
      gT.appendChild(el("line",{x1:ax1.toFixed(1),y1:ay1.toFixed(1),x2:ax2.toFixed(1),y2:ay2.toFixed(1),
        stroke:"var(--waveS)","stroke-width":2,"stroke-opacity":0.85}));
      function ah(cx,cy,sx,sy){ var px=-sy,py=sx;   // cabeza en (cx,cy) apuntando (sx,sy)
        gT.appendChild(el("polygon",{points:
          cx.toFixed(1)+","+cy.toFixed(1)+" "+(cx-hp*sx+hp*0.55*px).toFixed(1)+","+(cy-hp*sy+hp*0.55*py).toFixed(1)+
          " "+(cx-hp*sx-hp*0.55*px).toFixed(1)+","+(cy-hp*sy-hp*0.55*py).toFixed(1),
          fill:"var(--waveS)","fill-opacity":0.85})); }
      ah(ax2,ay2,r.tux,r.tuy); ah(ax1,ay1,-r.tux,-r.tuy);
      var pol=Math.abs(r.tuy)>Math.abs(r.tux)?"N–S":"E–O";
      var plbl=el("text",{x:(ax2+9*r.tux).toFixed(1),y:(ay2+9*r.tuy+3).toFixed(1),
        "font-size":10,"font-weight":"700",fill:"var(--waveS)","text-anchor":"middle"});
      plbl.textContent=pol; gT.appendChild(plbl);

      // marcador en el mapa (oscila transversalmente al pasar la S)
      r.mk=el("circle",{cx:r.x,cy:r.y,r:5,fill:r.col,stroke:"var(--card)","stroke-width":1.5});
      r.mkLbl=el("circle",{cx:r.x,cy:r.y,r:5,fill:"none",stroke:r.col,"stroke-width":2,"stroke-opacity":0});
      gT.appendChild(r.mk); gT.appendChild(r.mkLbl);
    });
    fig.appendChild(col);
    container.appendChild(fig);

    // línea-resumen con la razón explícita adelante/atrás
    var resumen=hEl("div","note"); resumen.style.marginTop="8px";
    resumen.style.fontSize="13px"; container.appendChild(resumen);

    // ---- barra de balance energético ----
    var bud=hEl("div","bud");
    bud.appendChild(hEl("div","lbl","Balance energético  E₀ = Eₛ + E_G + E_D"));
    var bsvg=el("svg",{viewBox:"0 0 700 46",preserveAspectRatio:"none"});
    var segEs=el("rect",{x:0,y:6,height:26,fill:"var(--es)"});
    var segEg=el("rect",{y:6,height:26,fill:"var(--eg)"});
    var segEd=el("rect",{y:6,height:26,fill:"var(--ed)"});
    var txEs=el("text",{y:26,"font-size":12,fill:"#fff","font-weight":"700"});
    var txEg=el("text",{y:26,"font-size":11,fill:"#3a2f00","font-weight":"700"});
    var txEd=el("text",{y:26,"font-size":12,fill:"#fff","font-weight":"700"});
    [segEs,segEg,segEd,txEs,txEg,txEd].forEach(function(e){bsvg.appendChild(e);});
    bud.appendChild(bsvg);
    var note=hEl("div","note","");
    bud.appendChild(note);
    container.appendChild(bud);

    // ---- falla + tip en el mapa ----
    var fBase=el("line",{stroke:"var(--edge)","stroke-width":3,"stroke-linecap":"round"});
    var fRupt=el("line",{stroke:"var(--fault)","stroke-width":4,"stroke-linecap":"round"});
    var tip=el("circle",{r:5,fill:"var(--fault)"});
    gT.appendChild(fBase); gT.appendChild(fRupt); gT.appendChild(tip);
    // leyenda de ondas en el mapa
    var lgP=el("rect",{x:8,y:8,width:12,height:8,fill:"var(--waveP)"});
    var lgPt=el("text",{x:23,y:15,"font-size":10,fill:"var(--ink)"}); lgPt.textContent="P (rápida, pequeña)";
    var lgS=el("rect",{x:8,y:20,width:12,height:8,fill:"var(--waveS)"});
    var lgSt=el("text",{x:23,y:27,"font-size":10,fill:"var(--ink)"}); lgSt.textContent="S (lenta, grande — domina)";
    gT.appendChild(lgP); gT.appendChild(lgPt); gT.appendChild(lgS); gT.appendChild(lgSt);

    // ================= física: SUMA EXPLÍCITA DE HUYGENS =================
    // Cada punto de la falla ES una fuente. Aporta un incremento de momento
    // (pulso positivo, área M0/N) que llega al receptor a azimut θ con retardo
    //   τ_i = t_i − (x_i/c)·cosθ       (t_i = tiempo de ruptura del punto i)
    // La traza del receptor = SUMA de esos N aportes. De ahí emerge todo:
    //   adelante los τ_i se apiñan → pulso alto y corto;
    //   atrás se separan → tren largo y bajo;  MISMO momento (área) en los 3.
    //   Apilamiento perfecto (τ_i iguales) en cosθ = 1/β → cono de Mach (β>1).
    var traces={}, PGAmax=1, Tw=1, dt=1, areaRef=1, SIG=1;
    function recompute(){
      var T0=P.lambda/P.c, Vr=P.beta*P.c, N=Math.max(3,P.nSources|0);
      var L=Math.min(P.L,300), half=L/2, i; SIG=0.5*T0;
      var src=[]; for(i=0;i<N;i++){var xi=-half+(i/(N-1))*L; src.push({x:xi,tr:(xi+half)/Vr});}
      var maxSpan=0;
      var dtPS=(RD/P.c)*(1-1/VPVS);      // la P llega ANTES que la S por este lapso
      var LEAD=dtPS+6*SIG;               // hueco reservado antes de la S (para la P)
      recs.forEach(function(r){
        var taus=[],tmin=1e9,tmax=-1e9;
        src.forEach(function(s){var tau=s.tr-(s.x/P.c)*Math.cos(r.theta);
          taus.push(tau); if(tau<tmin)tmin=tau; if(tau>tmax)tmax=tau;});
        r._taus=taus; r._shift=tmin-2*SIG-LEAD; var sp=tmax-tmin; if(sp>maxSpan)maxSpan=sp;
      });
      Tw=maxSpan+4*SIG+LEAD; dt=Tw/NS; PGAmax=1e-9;
      var pC=2*SIG+LEAD-dtPS;             // centro del pulso P (mismo para los 3 receptores)
      var NIND=Math.min(N,12), step=N/NIND;
      recs.forEach(function(r){
        var buf=new Float64Array(NS), n, s, indBufs=[];
        for(s=0;s<NIND;s++) indBufs.push(new Float64Array(NS));
        for(s=0;s<N;s++){
          var tau=r._taus[s]-r._shift, ii=Math.min(NIND-1,Math.floor(s/step));
          var n0=Math.max(0,((tau-3.2*SIG)/dt)|0), n1=Math.min(NS,((tau+3.2*SIG)/dt)|0);
          for(n=n0;n<n1;n++){var z=(n*dt-tau)/SIG, w=(1/N)*Math.exp(-z*z);
            buf[n]+=w; indBufs[ii][n]+=w;}
        }
        var pga=0,area=0,tp=0,na=NS,nb=0;
        for(n=0;n<NS;n++){var v=buf[n]; if(v>pga){pga=v;tp=n*dt;} area+=v*dt;}
        for(n=0;n<NS;n++){if(buf[n]>0.08*pga){if(n<na)na=n; if(n>nb)nb=n;}}
        // ONDA P: pulso pequeño y temprano (P menos energético que la S)
        var pbuf=new Float64Array(NS), SIGP=1.15*SIG, PA=APREL*pga;
        for(n=0;n<NS;n++){var zp=(n*dt-pC)/SIGP; pbuf[n]=PA*Math.exp(-zp*zp);}
        var ticks=[]; for(s=0;s<N;s++) ticks.push(r._taus[s]-r._shift);
        traces[r.key]={buf:buf,pbuf:pbuf,inds:indBufs,ticks:ticks,pga:pga,ppga:PA,
          area:area,dur:(nb-na)*dt,tpeak:tp,pC:pC};
        if(pga>PGAmax)PGAmax=pga;
      });
      areaRef=traces.lat.area || 1;
      recs.forEach(function(r){ drawFull(r); updateRead(r); });
      updateBudget();
      var ratio=traces.fwd.pga/traces.bwd.pga, nota;
      if(P.beta<0.999)
        nota="ideal (1+β)/(1−β)="+((1+P.beta)/(1-P.beta)).toFixed(1)+
          "×; aquí algo menor por banda finita";
      else
        nota="supershear: apilamiento en el cono de Mach θ_M="+
          (Math.acos(1/P.beta)*180/Math.PI).toFixed(0)+"°";
      resumen.innerHTML="<b>PGA Adelante / Atrás = "+ratio.toFixed(1)+"×</b> &nbsp;·&nbsp; "+
        "duración Atrás / Adelante = "+(traces.bwd.dur/traces.fwd.dur).toFixed(1)+
        "× &nbsp;·&nbsp; momento (área) ≈ igual &nbsp;·&nbsp; "+
        "<span style='color:var(--muted)'>"+nota+"</span>";
    }

    function yOf(v){ return 70 - (v / PGAmax) * 62; }   // línea base abajo, pulso hacia arriba
    function drawFull(r){
      var tr=traces[r.key], b=tr.buf, n, pts=[];
      for(n=0;n<NS;n++){ pts.push(((n/(NS-1))*320).toFixed(1)+","+yOf(b[n]).toFixed(1)); }
      r.full.setAttribute("points",pts.join(" "));
      // preview tenue del pulso P + posición de los rótulos P/S
      var pp=[]; for(n=0;n<NS;n++){ pp.push(((n/(NS-1))*320).toFixed(1)+","+yOf(tr.pbuf[n]).toFixed(1)); }
      r.pFull.setAttribute("points",pp.join(" "));
      r.lblP.setAttribute("x",((tr.pC/Tw)*320).toFixed(1));
      r.lblP.setAttribute("y",(yOf(tr.ppga)-3).toFixed(1));
      r.lblS.setAttribute("x",((tr.tpeak/Tw)*320).toFixed(1));
      r.lblS.setAttribute("y",(yOf(tr.pga)-3).toFixed(1));
      // aportes individuales (tenues): "cada punto de la falla es una fuente"
      var j=0,k;
      for(k=0;k<tr.inds.length;k++){
        var ib=tr.inds[k], seg=[], any=false;
        for(n=0;n<NS;n++){ if(ib[n]>0.002)any=true;
          seg.push(((n/(NS-1))*320).toFixed(1)+","+yOf(ib[n]).toFixed(1)); }
        var pl=r.indPool[j]||(r.indPool[j]=r.gInd.appendChild(
          el("polyline",{fill:"none",stroke:r.col,"stroke-width":0.8,"stroke-opacity":0.32})));
        pl.setAttribute("points",seg.join(" ")); pl.style.display=any?"":"none"; j++;
      }
      for(;j<r.indPool.length;j++) r.indPool[j].style.display="none";
      // marcas de arribo (una por punto de falla) — su separación = la directividad
      var m=0,mm;
      for(mm=0;mm<tr.ticks.length;mm++){
        var x=(tr.ticks[mm]/Tw)*320;
        var tk=r.tkPool[m]||(r.tkPool[m]=r.gTk.appendChild(
          el("line",{stroke:r.col,"stroke-width":1,"stroke-opacity":0.55})));
        tk.setAttribute("x1",x.toFixed(1)); tk.setAttribute("y1",72);
        tk.setAttribute("x2",x.toFixed(1)); tk.setAttribute("y2",76);
        tk.style.display=""; m++;
      }
      for(;m<r.tkPool.length;m++) r.tkPool[m].style.display="none";
    }
    function updateRead(r){
      var d=traces[r.key];
      // PGA relativo al máximo · duración · momento (área) relativo (≈1 en los tres)
      r.readEl.textContent="PGA "+(d.pga/PGAmax).toFixed(2)+"× · dur "+d.dur.toFixed(1)+
        " s · momento "+(d.area/areaRef).toFixed(2)+"×";
    }
    function updateBudget(){
      var es=Math.min(0.30,Math.max(0.05,P.esRad)), eg=0.08, ed=Math.max(0.02,1-es-eg);
      var W=700; segEs.setAttribute("x",0); segEs.setAttribute("width",(es*W).toFixed(1));
      segEg.setAttribute("x",(es*W).toFixed(1)); segEg.setAttribute("width",(eg*W).toFixed(1));
      segEd.setAttribute("x",((es+eg)*W).toFixed(1)); segEd.setAttribute("width",(ed*W).toFixed(1));
      txEs.setAttribute("x",(es*W/2).toFixed(1)); txEs.setAttribute("text-anchor","middle");
      txEs.textContent="Eₛ "+Math.round(es*100)+"%";
      txEg.setAttribute("x",(es*W+eg*W/2).toFixed(1)); txEg.setAttribute("text-anchor","middle");
      txEg.textContent=(eg>0.05?"E_G "+Math.round(eg*100)+"%":"");
      txEd.setAttribute("x",((es+eg)*W+ed*W/2).toFixed(1)); txEd.setAttribute("text-anchor","middle");
      txEd.textContent="E_D "+Math.round(ed*100)+"% (calor)";
      note.innerHTML="Solo <b>Eₛ</b> (radiada) forma los pétalos de ondas; se reparte "+
        "según la directividad. <b>E_D</b> se convierte en <b>calor</b> por fricción; "+
        "<b>E_G</b> es el costo de fracturar la roca.";
    }

    // ================= animación =================
    var t=0, playing=true, lastTS=null, raf=null;
    function wavefronts(){
      var T0=P.lambda/P.c, Vr=P.beta*P.c, N=Math.max(2,P.nSources|0), L=Math.min(P.L,300), xL=MCX-L/2;
      var Vp=P.c*VPVS, list=[],i,kk; var RMAX=360;
      for(i=0;i<N;i+=2){ // cada 2 subfuentes basta para el contexto visual
        var xi=xL+(i/(N-1))*L, ti=(xi-xL)/Vr;
        for(kk=0;kk<3;kk++){
          var rs=P.c*(t-ti-kk*T0);              // frente S (lento)
          if(rs>2&&rs<RMAX) list.push({x:xi,r:rs,op:0.16*(1-rs/RMAX),col:"var(--waveS)"});
          var rp=Vp*(t-ti-kk*T0);               // frente P (rápido -> va por delante)
          if(rp>2&&rp<RMAX) list.push({x:xi,r:rp,op:0.11*(1-rp/RMAX),col:"var(--waveP)"});
        }
      }
      var j=0,c;
      for(i=0;i<list.length;i++){ c=wpool[j]||(wpool[j]=gW.appendChild(el("circle",{fill:"none","stroke-width":1.2}))); j++;
        c.setAttribute("cx",list[i].x.toFixed(1)); c.setAttribute("cy",MCY); c.setAttribute("r",list[i].r.toFixed(1));
        c.setAttribute("stroke",list[i].col); c.setAttribute("stroke-opacity",list[i].op.toFixed(3)); c.style.display="";
      }
      for(;j<wpool.length;j++)wpool[j].style.display="none";
    }
    function faultUpdate(){
      var Vr=P.beta*P.c, L=Math.min(P.L,300), xL=MCX-L/2, xtip=xL+Math.min(Vr*t,L), act=Vr*t>0&&Vr*t<=L*1.02;
      fBase.setAttribute("x1",xL);fBase.setAttribute("y1",MCY);fBase.setAttribute("x2",xL+L);fBase.setAttribute("y2",MCY);
      fRupt.setAttribute("x1",xL);fRupt.setAttribute("y1",MCY);fRupt.setAttribute("x2",xtip);fRupt.setAttribute("y2",MCY);
      tip.style.display=act?"":"none"; tip.setAttribute("cx",xtip);tip.setAttribute("cy",MCY);
    }
    function revealTraces(){
      var idx=Math.min(NS-1,Math.max(0,(t/dt)|0));
      recs.forEach(function(r){
        var b=traces[r.key].buf, pb=traces[r.key].pbuf, pts=[],pp=[],n;
        for(n=0;n<=idx;n++){pts.push(((n/(NS-1))*320).toFixed(1)+","+yOf(b[n]).toFixed(1));
          pp.push(((n/(NS-1))*320).toFixed(1)+","+yOf(pb[n]).toFixed(1));}
        r.live.setAttribute("points",pts.join(" "));
        r.pLive.setAttribute("points",pp.join(" "));
        var x=(idx/(NS-1))*320, y=yOf(b[idx]);
        r.cur.setAttribute("cx",x.toFixed(1)); r.cur.setAttribute("cy",y.toFixed(1));
        // el marcador OSCILA transversal al rayo (cizalla S), ∝ amplitud del pulso
        var pv=traces[r.key].buf[idx]/PGAmax, osc=11*pv*Math.sin(t*9);
        r.mk.setAttribute("cx",(r.x+osc*r.tux).toFixed(1));
        r.mk.setAttribute("cy",(r.y+osc*r.tuy).toFixed(1));
        // destello del marcador cuando pasa el pico
        var near=Math.abs(t-traces[r.key].tpeak)<0.25;
        r.mkLbl.setAttribute("stroke-opacity",near?"0.9":"0");
        r.mkLbl.setAttribute("r",near?"11":"5");
      });
    }
    function frame(ts){
      if(lastTS==null)lastTS=ts; var d=(ts-lastTS)/1000; lastTS=ts;
      if(playing){ t+=d*P.speed; if(t>Tw)t=0; }
      wavefronts(); faultUpdate(); revealTraces();
      raf=requestAnimationFrame(frame);
    }

    recompute(); raf=requestAnimationFrame(frame);

    return {
      setParam:function(name,val){ if(!(name in P))return;
        P[name]=(typeof DEF[name]==="number")?+val:val;
        if(name==="esRad"){ updateBudget(); } else { recompute(); }
      },
      getParams:function(){var o={};for(var k in P)o[k]=P[k];return o;},
      play:function(){playing=true;}, pause:function(){playing=false;},
      toggle:function(){playing=!playing;return playing;},
      reset:function(){t=0;},
      destroy:function(){if(raf)cancelAnimationFrame(raf);container.innerHTML="";}
    };
  }
  global.SimBalanceEnergetico={crear:crear,DEFAULTS:DEF};
})(typeof window!=="undefined"?window:this);
