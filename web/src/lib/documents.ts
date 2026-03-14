/**
 * Documentos legislativos para el visor comparativo.
 * Boletín 2897-07 (moción original) vs Ley 19.948 (ley aprobada).
 */

export interface DocumentoLegislativo {
  id: string
  tipo: "boletin" | "ley"
  titulo: string
  subtitulo: string
  fecha: string
  /** Secciones del documento */
  secciones: SeccionDocumento[]
}

export interface SeccionDocumento {
  tipo: "encabezado" | "preambulo" | "articulo" | "transitorio" | "cierre"
  titulo?: string
  contenido: string
}

/** Boletín 2897-07: Moción original */
export const BOLETIN_2897_07: DocumentoLegislativo = {
  id: "2897-07",
  tipo: "boletin",
  titulo: "Boletín N° 2897-07",
  subtitulo: "Moción Parlamentaria",
  fecha: "2002",
  secciones: [
    {
      tipo: "encabezado",
      titulo: "Autores",
      contenido:
        "Moción de los diputados señores Uriarte, Álvarez, Barros, Forni, Kast, Pérez, don Ramón; Prieto, Urrutia, Von Mühlenbrock y de la diputada señora Marcela Cubillos.",
    },
    {
      tipo: "encabezado",
      titulo: "Materia",
      contenido:
        "Crea un procedimiento para eximir de responsabilidad en caso de extravío, hurto o robo de la cédula nacional de identidad y de otros documentos de identificación.",
    },
    {
      tipo: "preambulo",
      contenido:
        "Es un hecho de ordinaria ocurrencia en nuestro medio que muchas personas, por diversos motivos, extravían su cédula de identidad o su pasaporte, o se lo hurtan o roban. Nuestra legislación no prevé un procedimiento expedito y eficaz para esta situación, como sucede, en cambio, con algunos documentos mercantiles.\n\nLa falta de normas jurídicas precisas sobre la materia, significa en la práctica que la persona afectada debe iniciar una serie de trámites administrativos y judiciales, pérdida de tiempo y riesgo de verse eventualmente envuelto en algún acto delictivo, como suplantación de identidad y fraudes en operaciones comerciales.\n\nSi bien no es posible evitarle algún grado de preocupación a la persona que extravía su cédula, o que por desgracia se la hurtan o roban, es posible, en cambio, establecer un trámite administrativo que le ahorre tiempo y que le dé la seguridad de acreditar su inocencia en caso de un mal uso del carné extraviado, hurtado o robado.\n\nPara ello parece lo más lógico que el afectado concurra ante un notario, haga una declaración jurada, y el mismo notario se encargue de remitirla a una base de datos y a la justicia, en su caso, en la forma que se indica en el texto que sigue.\n\nPor estos motivos, venimos en presentar el siguiente",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 1°",
      contenido:
        "En caso de extravío, hurto o robo de una cédula de identidad o de otro documento de identificación otorgado en conformidad al artículo 4° N° 4°, de la ley N° 19.477, el afectado podrá efectuar una declaración jurada ante cualquier notario público.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 2°",
      contenido:
        "En la declaración jurada a que se refiere el artículo anterior, se indicará a lo menos, el lugar presumible del extravío, hurto o robo, y sus circunstancias, el número del documento, la individualización del afectado, y si, a juicio de éste, se trató de un extravío, hurto o robo.\n\nUna copia firmada por el afectado y autorizada será remitida por el notario al juez de letras o al ministerio público, que fueron competentes, de acuerdo con los antecedentes consignados en la declaración, en caso de tratarse de hurto o robo. Dicho documento constituirá una denuncia formal, que no requerirá ser ratificada judicialmente, sin perjuicio de la responsabilidad que pudiere afectar al declarante, en conformidad con las normas generales.\n\nAdemás, el notario remitirá, en cualquiera de los casos señalados en el artículo 1°, una copia autorizada de la declaración al registro a que se refiere el artículo 22 de la ley N° 19.628. A costa del afectado se podrá remitir la misma información a otras bases de datos.\n\nAl afectado se le otorgará copia autorizada de la misma declaración.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 3°",
      contenido:
        "Una vez cumplido lo dispuesto en el artículo anterior, y siempre que el afectado haya hecho una publicación a su costa en un diario de su elección, quedará exento de responsabilidad por los delitos que pudieran perpetrarse con la cédula extraviada, hurtada o robada, lo cual se entiende sin perjuicio de las facultades del juez o del fiscal, en su caso.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 4°",
      contenido:
        "Sin perjuicio de lo dispuesto en esta ley, el afectado solicitará ante el Servicio de Registro Civil e Identificación el nuevo documento de identificación que corresponda.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 5°",
      contenido:
        "El que utilizare maliciosamente un documento de identificación extraviado, hurtado o robado, será sancionado en la forma prevista en el artículo 196 del Código Penal. Si la utilización fuere un medio para cometer otro delito, se aplicará la pena mayor al delito más grave.",
    },
  ],
}

/** Ley 19.948: Texto aprobado y promulgado */
export const LEY_19948: DocumentoLegislativo = {
  id: "19948",
  tipo: "ley",
  titulo: "Ley N° 19.948",
  subtitulo: "Texto Promulgado",
  fecha: "12 de mayo de 2004",
  secciones: [
    {
      tipo: "encabezado",
      titulo: "Materia",
      contenido:
        "Crea un procedimiento para eximir de responsabilidad en caso de extravío, robo o hurto de la cédula de identidad y de otros documentos de identificación.",
    },
    {
      tipo: "preambulo",
      contenido:
        "Teniendo presente que el H. Congreso Nacional ha dado su aprobación al siguiente Proyecto de ley:",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 1°",
      contenido:
        "En caso de extravío, hurto o robo de una cédula de identidad, de un pasaporte, de un documento o título de viaje o de una licencia de conducir, el afectado deberá solicitar su bloqueo ante el Servicio de Registro Civil e Identificación, de conformidad con esta ley, tan pronto tenga noticia de dicha circunstancia.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 2°",
      contenido:
        "Salvo prueba en contrario, se presumirá, para todos los efectos legales, que el titular de dichos documentos no ha hecho uso de ellos en todo el tiempo posterior al día y hora del bloqueo a que se refiere el artículo anterior.\n\nPara los efectos de hacer valer la presunción a que se refiere el inciso precedente, bastará el respectivo comprobante de bloqueo expedido por el Servicio de Registro Civil e Identificación.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 3°",
      contenido:
        "El bloqueo de una cédula de identidad o de un pasaporte puede solicitarse de manera definitiva o temporal.\n\nLa solicitud de bloqueo definitivo es la efectuada por el titular del documento, ante cualquier oficina del Servicio de Registro Civil e Identificación y deberá contener:\n\na) Nombre completo y Rol Único Nacional;\nb) Motivo del bloqueo, el que no podrá ser otro que extravío, hurto o robo, y\nc) Firma del solicitante.\n\nSi el extravío, hurto o robo de los documentos a que se refiere esta ley, se produce en el extranjero, la solicitud de bloqueo definitivo podrá efectuarse ante la oficina consular respectiva, con las mismas formalidades requeridas en el inciso anterior.\n\nConstituye también una solicitud de bloqueo definitivo la realizada por vía electrónica utilizando firma electrónica avanzada, de conformidad con la ley.\n\nLa solicitud de una nueva cédula de identidad o pasaporte constituirá, por el solo ministerio de la ley, una solicitud de bloqueo definitivo del documento anterior.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 4°",
      contenido:
        "La solicitud de bloqueo temporal es la que se efectúa por vía telefónica o electrónica. El bloqueo así solicitado estará vigente hasta los dos días hábiles siguientes a aquel en que se solicita. Se podrá pedir la renovación de este bloqueo por una sola vez, dentro del último día del vencimiento del plazo. Con posterioridad a este plazo, se considerará como un nuevo bloqueo temporal.\n\nLa presunción a que se refiere el artículo 2° de esta ley beneficiará al titular del documento desde el momento de efectuada la solicitud de bloqueo temporal sólo si, dentro de la vigencia del plazo a que se refiere el inciso anterior, se procede a solicitar el bloqueo definitivo. Con posterioridad a este plazo, la presunción del artículo 2° sólo beneficiará al solicitante, a partir de la solicitud de bloqueo definitivo.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 5°",
      contenido:
        "Para proceder al bloqueo solicitado, el Servicio del Registro Civil e Identificación podrá regular internamente la exigencia de requisitos adicionales que permitan verificar la identidad de quien lo solicita y, resultando negativa tal verificación, denegar el bloqueo.\n\nCon todo, de no poder efectuar en el acto tal verificación, procederá a bloquear temporalmente el documento o a extender el bloqueo temporal que estuviere vigente, en ambos casos, por todo el tiempo que dura dicha verificación.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 6°",
      contenido:
        "El que obtenga el bloqueo previsto en esta ley, declarando falsamente en la solicitud la concurrencia de motivo legal para el mismo, será castigado con multa de 6 a 10 unidades tributarias mensuales.\n\nLo anterior es sin perjuicio de las sanciones penales que correspondan por el uso fraudulento del documento bloqueado, conforme a lo dispuesto en el párrafo 8° del Título IX del Libro Segundo del Código Penal.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 7°",
      contenido:
        "Cuando dentro de los hechos que constituyen un delito, aparezca que una persona sujeta a investigación criminal o imputada por dicho delito, se ha identificado con alguno de los documentos a que se refiere esta ley o, por la naturaleza del delito de que se trata, ha debido identificarse con ellos, los intervinientes en el proceso penal que soliciten en su contra una orden de detención, o arresto por falta de comparecencia, deberán hacer constar al tribunal que se ha consultado la base de datos del Servicio de Registro Civil e Identificación referida a bloqueos de que pudo haber sido objeto tal documento, lo que será considerado como un antecedente adicional a los restantes existentes para decretar cualquiera de dichas medidas.",
    },
    {
      tipo: "articulo",
      titulo: "Artículo 8°",
      contenido:
        "El Servicio de Registro Civil e Identificación tendrá disponible la información de bloqueo de documentos para cualquier persona, natural o jurídica, que desee consultarla.",
    },
    {
      tipo: "transitorio",
      titulo: "Artículo transitorio",
      contenido:
        "Respecto de aquellos delitos investigados o juzgados de conformidad con las normas del Código de Procedimiento Penal, el juez del crimen, previo a decretar una orden de arresto o detención en los casos señalados en el artículo 7° de esta ley, deberá hacer constar en la causa que se ha consultado la base de datos a que se refiere dicho artículo.",
    },
    {
      tipo: "cierre",
      contenido:
        "Santiago, 12 de mayo de 2004.— RICARDO LAGOS ESCOBAR, Presidente de la República.— Luis Bates Hidalgo, Ministro de Justicia.— José Miguel Insulza Salinas, Ministro del Interior.",
    },
  ],
}

/** Todos los pares de documentos disponibles para comparación */
export const PARES_DOCUMENTOS = [
  {
    boletin: BOLETIN_2897_07,
    ley: LEY_19948,
    resumen:
      "La moción original proponía un sistema basado en declaración jurada ante notario. La ley aprobada cambió completamente el mecanismo: reemplazó al notario por el Servicio de Registro Civil, introdujo un sistema de bloqueo (definitivo y temporal), y amplió los documentos cubiertos a pasaportes, títulos de viaje y licencias de conducir.",
  },
]
