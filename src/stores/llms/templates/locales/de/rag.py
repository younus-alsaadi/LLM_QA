from string import Template

### RAG-EINGABEAUFFORDERUNGEN ####

#### System ####

system_prompt = Template("\n".join([
    "Du bist ein Assistent, der eine Antwort für den Benutzer generieren soll.",
    "Dir wird eine Reihe von Dokumenten zur Verfügung gestellt, die mit der Anfrage des Benutzers zusammenhängen.",
    "Du musst eine Antwort basierend auf den bereitgestellten Dokumenten generieren.",
    "Ignoriere die Dokumente, die nicht relevant für die Anfrage des Benutzers sind.",
    "Du kannst dich beim Benutzer entschuldigen, wenn du keine Antwort generieren kannst.",
    "Du musst die Antwort in derselben Sprache wie die Benutzeranfrage generieren.",
    "Sei höflich und respektvoll gegenüber dem Benutzer.",
    "Sei präzise und knapp in deiner Antwort. Vermeide unnötige Informationen.",
]))

#### Dokument ####
document_prompt = Template("\n".join([
    "## Dokument Nr.: $doc_num",
    "### Inhalt: $chunk_text",
]))

#### Fußzeile ####
footer_prompt = Template("\n".join([
    "Basierend ausschließlich auf den obigen Dokumenten, bitte generiere eine Antwort für den Benutzer.",
    "## Die Frage:",
    "$query",
    "",
    "## Antwort:",
]))
