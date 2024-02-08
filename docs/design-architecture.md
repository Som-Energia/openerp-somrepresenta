# Design choices

All decisions are revocable.
Annotate reasons and also drawbacks to consider the novelty of new arguments.

## Architecture

- **Wrap domain logic under erp entry points**
    - Single call to erp is more efficient than many combined search, read...
    - Removes the need of extended transactions covering several ops
    - Decouples OV from the ERP internals, enabling refactors in ERP without having to consider code in OV
- **Use ERP team conventions for inner ERP names (data models, inner methods and fields...)**
    - They eventually will be maintained by ERP, and better to adhere to their conventions
    - :sad: Legacy and reused erp models have crap names that do not relate to the concept we meant
- **Use OV domain vocabulary for external ERP objects (ov entry points, returning field names, expected errors...)**
    - We are using models with different semantics inside and outside ERP
        - ie. OV users are both `res_partners` (clients?) and `res_users` (staff)
    - Different naming also will decouple semantically internal representation.
- **Split model objects and api objects.**
    - Because their different nature use a naming prefix/decorator to mark external entrypoints.
    - TODO: Review Proposal
- **Double ERP data source with a dummy data source:**
    - Starting with a dummy api, enables parallel development of the ui and erp sides
    - Dummy serves as prototype for the used protocol
    - Enables decoupled testing
- **Name the layers ui-api-erp**
    - Using _frontend_ may mean both api and ui
    - Using _backend_ may mean both api and erp
    - :sad: erp also provides an api -> just name it
    - TODO: current ui and api are in `frontend`/`backend` directories
- **Keep api layer thin:**
    - As we move business logic towards ERP, this layer should do no more than a proxy
    - Exceptions:
        - Bidirectional data validation
        - API documentation (FastAPI)
        - Authentication (will be thinner when we have Auth Server)
        - ERP Doubling for testing purposes
- **Let input validation to FastApi**
    - Documentation and model serialization comes for free
- **Use same or similar schemas in erp and api layers**
    - We can reuse the same schema to validate ERP outputs and API outputs
    - In most cases the api layer will be just a forwarding
- **Name the data backend as data source**
    - Avoid also _backend_
    - May not be erp (dummy)
    - :-( Voki: i do not like "data source". What about domain, business... (i named it "data source" myself, but i don't like it)
- **Enumerations are not passed arround translatable human strings but as internal enum name string:**
    - The ui may choose to represent the enum value as an icon or color or use to take decissions to show/hide dependent attributes, if the value comes as translated string is hard to match the cases
    - Usually the translations are only needed at the user service layer
    - :-( Sometimes the backend also needs the translation (to make reports, sending emails...), in those cases the translations have to be done in both sides


## Translations

- **Use IDs and not original strings to name translateable texts**
    - Faster to look up
    - No spacing or lining differences
    - More stable to changes in the text
    - :sad: harder to understand what the text is in code -> Use good names!!
- **Use `UPPER_CASE_IDS` to reference the translations**
    - Easier to spot unstranslated strings
    - :sad: Buttons use uppercasing. Not so spottable.
    - :sad: Spottability only works with first translation -> Let the rest, weblate to take care
- **Use namespaces for string ids**
    - They provide context
    - Better naming within the context
    - Strings are grouped in the translation file
    - :sad: Often result in long ID's.
- **Bind translation namespaces to ui components**
    - Easy to get the context for a text
    - :sad: Makes hard to reuse texts among components
- **Spanish as reference language**
    - The reference language is the one shown in weblate as starting point for the translation
    - English would be a more standard lingua franca but we have no interest in having English translations
    - Lingua franca for Euskara and Galician translators is Spanish.
- **In code, only fill reference language, the rest in weblate**
    - It is hard to maintain as code sincronicity among languages
    - Often we fill Catalan or Spanish and left the other in blank
    - Weblate detects untranslated ids, you won't misspell them
    - Weblate provides context and the other languages as reference
- **Exception: In code, fill both, Spanish and Catalan**
    - Because often texts from business come in our native language, Catalan
    - Should be an exception, better to fill it in weblate
    - But avoid translate
- **Translate just reference language in code, let the rest for weblate**
    - When adding strings in code is hard to keep track of the translations you missed
    - In other project, we add sometimes the string in spanish and others in catalan, generating holes and incoherences in both
    - It is easy misspell ids, in different files, weblate does not.
    - Exception: Often is easier for us to write original texts in Catalan in that case fill both Spanish and Catalan, but always provide Spanish and left the rest to Weblate
- **Having spanish as reference and fallback language**
    - English could be an more standard lingua franca but is not a priority language in our programs
