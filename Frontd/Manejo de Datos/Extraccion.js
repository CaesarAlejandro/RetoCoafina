//------------------------------ Parte de Extracciom--------------

// Funcion que da informacion sobre el JSON (claves del json)
function propiedades(json){
    let extractor = json.flatMap(obj => Object.keys(obj))
    let listado = new Set(extractor)
    return listado
}


// Funcion que determina el valor de una clave en concreto
function extraerValor(json, propiedad){
    let almacen = json.map(obj => obj[propiedad])
    return almacen
}

// Devuelve un objeto que contiene todas las claves con todos los valores
function listaPropiedad(json, ...props ){
    let diccionario = {}
    props.forEach(prop => {
        diccionario[prop] = json.map(obj => obj[prop]);
    });
    return diccionario;
}

//------------------------------------------------------------------------

//----------------------Parte de Almacenamiento-------------------

class Organizador{
    constructor(diccionario) {
        this.diccionario = diccionario
    }
    getClaves(){
        return Object.keys(this.diccionario)
    }
    getValues(clave){
        return this.diccionario[clave] || [];
    }
    combinar(){
        return Object.values(this.diccionario).flat()
    }
    totalElementos(){
        return this.combinar().length
    }
    getDiccionario(){
        return this.diccionario
    }
    getAllValues(){
        return Object.values(this.diccionario).flat()
    }
}


//-------------------------------------------------------------------------------

//---- Parte de graficacion-------------------

function transformarCERN(json) {
    const bins = json.bins;
    const data = json.data.counts;
    const errors = json.data.errors;
    const signal = json.signal.counts;
    const backgrounds = json.backgrounds;

    return bins.map((bin, i) => {
        const fila = {
            BIN: bin,
            DATA_COUNT: data[i],
            DATA_ERROR: errors[i],
            SIGNAL_COUNT: signal[i],
            PERIODO: json.period,
            LUMINOSIDAD: json.lumi,
            X_AXIS_LABEL: json.x_axis_label,
            Y_AXIS_LABEL: json.y_axis_label
        };

        backgrounds.forEach((bg, index) => {
            fila[`BACKGROUND_${index + 1}_LABEL`] = bg.label;
            fila[`BACKGROUND_${index + 1}_COUNT`] = bg.counts[i];
        });

        return fila;
    });
}

const descripciones = {
    BIN: "Valor del bin (intervalo en GeV para la masa invariante 4l).",
    DATA_COUNT: "Número de eventos observados en los datos reales.",
    DATA_ERROR: "Incertidumbre estadística asociada a los datos.",
    SIGNAL_COUNT: "Número de eventos esperados del modelo de señal (ej. Higgs a 125 GeV).",
    PERIODO: "Periodo de adquisición de datos (ej. 2015-2016).",
    LUMINOSIDAD: "Luminosidad integrada del experimento (en fb⁻¹).",
    X_AXIS_LABEL: "Etiqueta del eje X (ej. Masa Invariante 4l en GeV).",
    Y_AXIS_LABEL: "Etiqueta del eje Y (ej. Eventos por bin).",
    BACKGROUND_1_LABEL: "Descripción del primer fondo simulado (ej. Z, tt̄, VVV).",
    BACKGROUND_1_COUNT: "Número de eventos esperados para el primer fondo.",
    BACKGROUND_2_LABEL: "Descripción del segundo fondo simulado (ej. ZZ*).",
    BACKGROUND_2_COUNT: "Número de eventos esperados para el segundo fondo."
};


function graficar(contenedor, ejex, ejey, opciones){

    const anchoMinimo = 1800;
    const anchoPorDato = 10;
    const width = Math.max(anchoMinimo, ejex.length * anchoPorDato);
    const height = 1500

    const svg = d3.select(contenedor)
                  .append("svg")
                  .attr("width", width)
                  .attr("height", opciones.height)


    const xScale =d3.scaleBand()
                    .domain(ejex)
                    .range([opciones.margin.left, width - opciones.margin.right])
                    .padding(0.1);

    const yScale = d3.scaleLinear()
                     .domain([0, d3.max(ejey)])
                     .range([opciones.height - opciones.margin.bottom, opciones.margin.top])
    svg.append("g")
        .attr("transform", `translate(0, ${opciones.height - opciones.margin.bottom})`)
        .call(d3.axisBottom(xScale));

    svg.append("g")
        .attr("transform", `translate(${opciones.margin.left}, 0)`)
        .call(d3.axisLeft(yScale));

    const datos = ejex.map((c,i) => ({clave: c, valor: ejey[i]}))

    svg.selectAll("rect")
        .data(datos)
        .enter()
        .append("rect")
        .attr("x", d => xScale(d.clave))
        .attr("y", d => yScale(d.valor))
        .attr("width", xScale.bandwidth())
        .attr("height", d => opciones.height - opciones.margin.bottom - yScale(d.valor))
        .attr("fill", opciones.color || "steelblue")
        .attr("stroke", "#0d47a1")
        .attr("font-family", "Consolas, monospace")

    svg.selectAll("text")
        .data(datos)
        .enter()
        .append("text")
        .attr("x", d => xScale(d.clave) + xScale.bandwidth()/2)
        .attr("y", yScale(d.valor) - 5)
        .attr("text-anchor", "middle")
        .text(d => d.valor)
}


