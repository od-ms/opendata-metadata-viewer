---
toc: false
title: Open Data
theme: [wide]
---

# Open Data Datensätze Münster

```js
import {DonutChart} from "./components/donutChart.js";
import {Swatches} from "./components/swatches.js";
// import {bigNumber} from "./components/bigNumber.js";

const regex = /\s*".*$/  // /("\s*|\(\d+\))/gi;
const coerceRow = function(d) {
    // Lösche die IDs aus den Referenzwerten
    for (const key of ['Tags', 'Groups']) {
        if (d[key]) {
            d[key] = d[key].substring(1,500).replace(regex, "");
        }
    } 
    return d;
}
const enhanceRessourceData = function(row) {
    const url = row["ResourceUrl"] ? row["ResourceUrl"].substring(8) : "";
    const typelist = [
        [/^[^\/]*github/i, 'github'],
        [/^www.stadt-muenster.de\/ows\/mapserv/i, 'geosrv'],
        [/^geo\d*.stadt-muenster.de/i, 'geosrv'],        
        [/^www.stadt-muenster/i, 'stadt'],
        [/^opendata.stadt-muenster/i, 'opendata'],
        [/^oparl.stadt-muenster.de/i, 'fachanw'],
        [/^wahlen.citeq.de/i, 'fachanw'],
    ];
    for (const [regex, type] of typelist) {
        if (regex.test(url)) {
            row["Hosting"] = type;
            break;
        }
    }
    if (! row["Hosting"]) {row["Hosting"]="extern"}
    for (const key of ['DDLicense']) {
        if (row[key]) {
            row[key] = row[key].substring(1,500).replace(regex, "");
        }
    } 
    return row;
}
const ressourceData = FileAttachment("data/ressourcen.csv").csv({typed: true}).then((D) => D.map(enhanceRessourceData));
const rawInputData = FileAttachment("data/datensaetze.csv").csv({typed: true}).then((D) => D.map(coerceRow));
const anlagenListeGefiltert = rawInputData;
```

```js
// Extract Earliest and Latest Date from CSV File
const dateColumn = rawInputData.map(function(d) { return d.Created });
const beginDate = dateColumn.sort(d3.ascending)[0];
const endDate = dateColumn.sort(d3.descending)[0];
```


<div class="card" style="height: 120px;overflow:hidden">
${resize((width, height) => zeitverlauf(width, height))}
</div>

```js
function zeitverlauf(width, height) {return Plot.plot({
    height:120,
    width,
  marks: [
    Plot.tickX(rawInputData, {
        x: "Created",
        stroke: {value: "Tags"},
        channels: {
            Title: {
                value: "Title",
                label: ""
            },
        //    Tags: "Tags",
            Groups: "Groups",
            License: "License", 
            ExtraQuelle:  {
                value: "ExtraQuelle",
                label: "Quelle"
            },
            NutzbareSpeicherkapazitaet:  {
                value: "NutzbareSpeicherkapazitaet",
                label: "Speicherkapazität"
            },
        },
        tip: { 
            dy:-40,
            anchor: "top",
            format: {
                Title: true,
                Created: true,
                x: "%d. %b %Y",
                ExtraQuelle: true,
                Tags: d => d.toString(), 
                NutzbareSpeicherkapazitaet: d => d.toString() + " kWh", 
            }
        }}),
    Plot.crosshairX(rawInputData, {x: "Created", color: "red", opacity: 1})
  ]
})
}
```


```js
// Hilfsfunktionen für die Pie Charts

function calcDonutSum(field, dataset) {
    // Berechnung der Prozentualen Anteile in den Pie Charts bzw Donuts
    // Anleitung für d3.rollups: https://observablehq.com/@d3/d3-group
    return d3.rollups(
        dataset.filter((row) => row[field]!=null), 
        v => v.length, 
        d => d[field]
    ).map(([name, value]) => ({name, value}));
}

function myDonut(data, name, cols) {
    console.log("data", data )
    const ress= data.map(function (d) {
        var einheit ="";
        return [d.name + ' ('+Math.floor(d.value)+einheit+')']});
    return html`
    ${resize(width => DonutChart(data, {centerText: name, width, colorDomain: cols, colorRange: cols}))}
    ${Swatches(d3.scaleOrdinal(ress, cols))}
    `;
}
```


## Datensätze Verteilung

<div class="grid grid-cols-3">
  <div class="card ">${myDonut(calcDonutSum('License',anlagenListeGefiltert), "Lizenz", d3.schemePaired)}</div>
  <div class="card ">${myDonut(calcDonutSum('Tags',anlagenListeGefiltert), "Kategorie", d3.schemeObservable10)}</div>
  <div class="card ">${myDonut(calcDonutSum('ExtraQuelle',anlagenListeGefiltert), "Amt", d3.schemeTableau10)}</div>
</div>

## Ressourcen Verteilung

<div class="grid grid-cols-3">
  <div class="card ">${myDonut(calcDonutSum('Hosting',ressourceData), "Hosting", d3.schemePaired)}</div>
  <div class="card ">${myDonut(calcDonutSum('Format',ressourceData), "Dateiformat", d3.schemeObservable10)}</div>
  <div class="card ">${myDonut(calcDonutSum('DDLicense',ressourceData), "Lizenz", d3.schemeTableau10)}</div>
</div>


## Datensätze

```js
// Visuelle Darstellung in der Tabellenspalte "Leistung"

function sparkbar(max) { 
   // logarithmic sparkbar
  return (x) => htl.html`<div style="
    background: var(--theme-green);
    color: black;
    font: 10px/1.6 var(--sans-serif);
    width: ${100 * Math.log(x+1)/Math.log(max+1)}%;
    float: right;
    padding-right: 3px;
    box-sizing: border-box;
    overflow: visible;
    display: flex;
    justify-content: end;">${Math.floor(x).toLocaleString("de-DE")}kWh`
}

// Create search input (for searchable table)
const tableSearch = Inputs.search(anlagenListeGefiltert);
const tableSearchValue = view(tableSearch);
```


<div class="card" style="padding: 0">
  <div style="padding: 1em">
    ${display(tableSearch)}
  </div>
  <div style="padding: 1em">
  ${display(Inputs.table(tableSearchValue, {
    rows: 18,
    columns: [
        "Created",
        "Modified",
        "NodeID",
        "Title",
        "Groups", 
        "Tags",
        "Author",
        "ExtraQuelle",
        "URL"
    ],
    width: {
        Created: 70,
        Modified: 70,
        NodeID: 50
    },
    format: {
        URL: id => htl.html`<a href="${id}" target=_blank>${id}</a>`,
        NodeID: d => d.toString(), 
        Created: d3.utcFormat("%d.%m.%Y"),
        Modified: d3.utcFormat("%d.%m.%Y")
    }
  }
  ))}
    </div>
</div>

## Ressourcen

<div class="card" style="padding: 0">
  <div style="padding: 1em">
  ${display(Inputs.table(ressourceData, {
        rows: 18,
        columns: [
            "Hosting",
            "Format",            
            "NodeID",
            "LfdNr",
            "ResourceName",
            "ResourceUrl",
            "DDLicense",
            "ResourceTypDetail"
        ],
    width: {
        Hosting: 70,
        NodeID: 50,
        Format: 50,
        LfdNr: 60,
    },
      format: {
            ResourceUrl: id => htl.html`<a href="${id}" target=_blank>${id}</a>`,
            NodeID: d => d.toString(),
        }
  }
  ))}
    </div>
</div>

<div class="card">
<table style="opacity:0.8">
<tr><th colspan="2">Information zu den dargestellten Daten</th></tr>
<tr><td>Datenstand:</td><td>${endDate.toLocaleDateString("de-DE")}</td></tr>
<tr><td>Datenquelle:</td><td><a href="https://opendata.stadt-muenster.de">Stadt Münster / citeq</a></td></tr>
<tr><td>Lizenz:</td><td><a href="https://www.govdata.de/dl-de/by-2-0">Datenlizenz Deutschland – Namensnennung – Version 2.0</a></td></tr>
<tr><td>Datendownload:</td><td><a href="https://opendata.stadt-muenster.de"> Open Data Portal Münster</a></td></tr>
</table>

</div>