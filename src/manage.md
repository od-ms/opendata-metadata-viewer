---
theme: dashboard
title: SQL Test
toc: false
---

# Open Data Münster Monitoring

```js
// import { DuckDBClient } from 'npm:@cmudig/duckdb'
// import { SummaryTable } from "npm:@observablehq/summary-table"

// LADE die CSV in DUCKDB
import {utcParse} from "npm:d3-time-format";

const parseDate = utcParse("%Y-%m-%dT%H:%M:%S.%LZ");
const coerceRow = function(d) {

    for (const key of ['NodeID']) {
        d[key] = Number(d[key]);
    } 
    for (const key of ['Created']) {
        //d[key] = parseDate(d[key]);
    } 
    for (const key of ['Description', 'Beschreibung']) {
        delete d[key];
    } 
    return d;
}

const db = DuckDBClient.of({
    datensaetze: FileAttachment('data/datensaetze.csv').csv({
      //  normalize_names=true
       // delimiter: ',', 
    }).then((D) => D.map(coerceRow)),
        ressourcen: FileAttachment('data/ressourcen.csv').csv({
       // delimiter: ',', 
    }).then((D) => D.map(coerceRow))
});
```

```js 
const res2 = await db.query("SELECT Groups, Author, ExtraQuelle Datenquelle, count(*), min(NodeID) FROM  datensaetze WHERE Groups LIKE '\"Stadt%' GROUP BY Groups, Author, Datenquelle ORDER BY Datenquelle");
const selectedFields2 = view(Inputs.table(res2));
```

```js 
const res3 = await db.query("SELECT NodeID, Created, Title, Groups, Author, DDPublisher, DDOriginator, ExtraQuelle Datenquelle FROM datensaetze WHERE  Groups LIKE '\"Stadt M%'  AND Datenquelle = ''");
```


<div class="card" style="padding: 0">
  <div style="padding: 1em">
  ${display(Inputs.table(res3, {
      sort: "NodeID",
      reverse: true,
      rows: 18,
      header: 
        {
          NodeID: "ID/Link"
          },
        width: {
            NodeID: 50,
            Created: 80,
            Title: 200},
        format: {
//            Id: id => htl.html`<a href="https://www.marktstammdatenregister.de/MaStR/Einheit/Detail/EinheitDetailDrucken/${id}" target=_blank>${id}</a>`,
            NodeID: id => htl.html`<a href="https://opendata.stadt-muenster.de/node/${id}/edit" target=_blank>${id}</a>`,
            Plz: d => d.toString(), 
            Bruttoleistung: (d) => (d + "kW"),
            Created: v => v.substring(0,10), //d3.utcParse("%Y-%m-%dT%H:%M:%S+"),
        }
    }
  ))}
    </div>
</div>


```js 
// ## Verfügbare Datenfelder
// "describeColumns" ist cool, aber brauchen wir nicht, weil "SUMMARIZE" ist noch besser
// const selectedFields = view(Inputs.table(db.describeColumns({table: "batteries"})))
```

## Zusammenfassung der Ressourcen
```js 
const resr = await db.query("SUMMARIZE ressourcen");
const selectedFieldsR = view(Inputs.table(resr));
```


## Zusammenfassung der Datenfelder
```js 
const res = await db.query("SUMMARIZE datensaetze");
const selectedFields = view(Inputs.table(res));
```

Ausgewählte Felder:
```js 
view(selectedFields )
```




## Felder mit mehr als 1 Wert
```js
function filterF(res) {
    var fields = []
    for (const row of res) {
        if (row.approx_unique > 1) {
            fields.push(row.column_name)
        } 
    } 
    return fields
}
const interesting_fields = filterF(res)

display(interesting_fields)
```

## Alle Daten
```js 
display(Inputs.table(db.query("SELECT " + interesting_fields.join(',') + " FROM datensaetze")));
```
test