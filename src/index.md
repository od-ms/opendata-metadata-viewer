---
theme: dashboard
title: SQL Test
toc: false
---

# Stromspeicher in Münster

```js
// import { DuckDBClient } from 'npm:@cmudig/duckdb'
// import { SummaryTable } from "npm:@observablehq/summary-table"

// LADE die CSV in DUCKDB
import {utcParse} from "npm:d3-time-format";

const parseDate = utcParse("%Y-%m-%d");
const coerceRow = function(d) {

    for (const key of ['Node-ID']) {
        d[key] = Number(d[key]);
    } 
    for (const key of ['Description']) {
        delete d[key];
    } 
    return d;
}

const db = DuckDBClient.of({
    datensaetze: FileAttachment('data/datensaetze.csv').csv({
       // delimiter: ',', 
    }).then((D) => D.map(coerceRow))
});
```


```js 
// ## Verfügbare Datenfelder
// "describeColumns" ist cool, aber brauchen wir nicht, weil "SUMMARIZE" ist noch besser
// const selectedFields = view(Inputs.table(db.describeColumns({table: "batteries"})))
```




## Zusammenfassung der Felder
```js 
const res = await db.query("SUMMARIZE datensaetze");
const selectedFields = view(Inputs.table(res));
```

Ausgewwählte Felder:
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