d3.json("../Manejo de Datos/datos.json").then( datos => {
    const claves = Array.from(propiedades(datos))
    const selectX =document.getElementById("ejeX")
    const selectY = document.getElementById("ejeY")

    claves.forEach(clave => {
        const optionX = document.createElement("option")
        optionX.value = clave
        optionX.textContent = clave
        selectX.appendChild(optionX)

        const optionY = document.createElement("option")
        optionY.value = clave
        optionY.textContent = clave
        selectY.appendChild(optionY)

    })
    selectX.addEventListener("change", intentarGraficar);
    selectY.addEventListener("change", intentarGraficar)

    function intentarGraficar(){
        const claveX = selectX.value
        const claveY = selectY.value

        if (claveX && claveY && claveX!== claveY){
            const diccionario = listaPropiedad(datos, claveX, claveY)
            const organizar = new Organizador(diccionario)

            const ejex = organizar.getValues(claveX)
            const ejey = organizar.getValues(claveY)

            if (ejex.length === ejey.length){
                d3.select("#grafica").selectAll("*").remove()

                const opciones ={
                    width: 500,
                    height: 300,
                    color: "steelblue",
                    margin: {top: 20, right: 20, bottom: 30, left: 40}
                }
                graficar("#grafica", ejex, ejey, opciones);
            }
        }
            else{
            console.warn("Las listas tiene diferente longitud")
            }

    }
})