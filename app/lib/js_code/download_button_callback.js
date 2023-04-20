function table_to_csv(datatable) {
    const columns = Object.keys(datatable.source.data)
    const nrows = datatable.source.get_length()
    const lines = [columns.join('`').replaceAll(/,/g,' ').replaceAll(/`/g,',')]
    
    for (let i = 0; i < nrows; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j]
            const val = datatable.source.data[column][i]
                    if (column == 'Date') {
                        row.push(new Date(val).toLocaleDateString("en-US"))}
                        else
                        row.push(val.toString())}
    lines.push(row.join(','))
    }
return lines.join('\n').concat('\n')
}

const filename = 'data.csv'
const filetext = table_to_csv(datatable)
const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename)
} else {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.target = '_blank'
    link.style.visibility = 'hidden'
    link.dispatchEvent(new MouseEvent('click'))
}