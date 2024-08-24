# :radio: :computer: WilCo - Radio Assistant - Radio Transcriptor 

Wilco es un servicio compuesto por una red multimodal que combine un modelo de speach to text con un LLM (como los que la API de OpenAI entrega) y nuestra propia aplicación API/SDK. Desde ella, podremos configurar un asistente capaz de llevar un registro de las conversaciones en el canal, definir comandos o “palabras clave” para dar instrucciones a un asistente y así realizar reportes o llamados de emergencia.  

Preliminarmente esta pensado en dos aplicaciones:

- RadioTranscriptor: Aplicación de escritorio modelo Speech to Text.
- RadioGPT: Aplicación Web LLM + Panel de control para informes y comandos.

---

### :pencil: Wilco Radio Transcriptor

El RadioTranscriptor es una aplicación de escritorio para convertir el audio de transmisiones de radio en texto escrito. Permite separar el texto en fragmentos correspondientes a cada clip de audio, registrar estos clips junto con sus respectivos textos y, en el futuro, identificar a los autores de cada clip. Además, facilita la detección de clips que forman parte del mismo contexto con la ayuda de un modelo de lenguaje grande (LLM), asegurando que no se pierda información valiosa durante el proceso de transcripción.
