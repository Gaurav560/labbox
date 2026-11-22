# Atlas, the guide of the Deccan Science Museum

Atlas is a Spring Boot 4 application that answers museum visitors with the help of a language model, through
Spring AI 2.0. Each chapter has its own copy of the project, in a folder named like the chapter (`01-why-ai`,
`02-prompts`, ...), so you can always go back and compare.

Run a chapter's app in one terminal:

    cd 01-why-ai && mvn -q -o spring-boot:run

and try it from a second terminal (click +):

    curl -s "localhost:8080/ask?q=Hello"; echo

The model is reached through the LabBox gateway: your lab machine has OPENAI_BASE_URL and OPENAI_API_KEY set, and
the key only works there. The course's models are called ai-chat and ai-embed.
