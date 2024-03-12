main_topics = [
    "Economía",
    "Salud",
    "Educación",
    "Medio ambiente",
    "Derechos civiles",
    "Inmigración",
    "Seguridad nacional",
    "Política exterior",
    "Empleo",
    "Criminalidad",
    "Impuestos",
    "Bienestar social",
    "Tecnología",
    "Energía",
    "Vivienda",
    "Corrupción",
    "Libertad de prensa",
    "Igualdad de género",
    "Diversidad y discriminación",
    "Pobreza",
    "Infraestructura",
    "Religión",
    "Derechos de las minorías",
    "Paz y conflicto",
    "Defensa",
    "Legislación",
    "Presupuesto",
    "Justicia",
    "ETA",
    "Historia reciente de España",
    "Terrorismo",
    "Acusaciones políticas",
    "Campaña electoral",
]

sentiment = [
    "Enojo",
    "Frustración",
    "Pasión",
    "Entusiasmo",
    "Preocupación",
    "Confianza",
    "Desesperación",
    "Optimismo",
    "Satisfacción",
    "Escepticismo",
    "Desdén",
    "Empatía",
]

lenguaje = [
    "Lenguaje formal",
    "Lenguaje técnico",
    "Lenguaje emocional",
    "Lenguaje persuasivo",
    "Lenguaje retórico",
    "Lenguaje bipartidista",
    "Lenguaje partidista",
    "Lenguaje populista",
    "Lenguaje de consenso",
    "Lenguaje de confrontación",
    "Lenguaje de compromiso",
    "Lenguaje de promesas",
    "Lenguaje de crítica",
    "Lenguaje de estadísticas",
    "Lenguaje de datos",
    "Lenguaje de debate",
    "Lenguaje de discurso público",
    "Lenguaje de campaña",
    "Lenguaje de legislación",
    "Lenguaje de negociación",
]


prompt = f"""Analiza las siguientes transcripciones de textos de políticos, y respóndeme a las preguntas que te propongo en formato json. Las claves del formato json son politican_name, political_party, date, length, summary, main_topics, sentiment, lenguaje y used_words. Para sus valores es muy importante que tengas en cuenta las siguientes condiciones : 
Para la key main_topics solo y solo si, pueden ser valores que se encuentren en el siguiente array. Esto significa que aunque encuentres otros main_topics, solo debes coger los que esten en este array y sean mas similares a los que has encontrado {main_topics}
Recuerda que los valores ademas tienen que tener un porcentaje que corresponda al tiempo que se habla de ellos en la transcripción. Para la key sentiment solo puede ser uno o varios de los siguientes array. Esto significa que aunque encuentres otros sentiments, solo debes coger los que esten en este array: {sentiment}. 
Para la key lenguaje solo puede ser uno o varios de los siguientes array. Esto significa que aunque encuentres otros lenguajes, solo debes coger los que esten en este array:  {lenguaje}. 
Para la key used_words coge las palabras politicas que mas se usen durante la transcripción. Las transcripción es la siguiente, y ya tiene el nombre del politico, el partido al que pertenece, la url, la fecha, y la duracion. Esto tambien tienes que incluirlo en el json que me das como respuesta. Además tienes que incluir un resumen corto de la transcripcion para la key summary. Recuerda tener en cuenta las limitaciones y solo coger valores de los arrays para las keys que lo necesitan: {transcription}
"""
