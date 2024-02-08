# Error handling policy

## ERP

- In ERP we discriminate among regular model methods and entry points.
- Entry points are the ones called by the API, and should be guarded by the `www_entry_point` decorator
- **Important:** Just wrap the entrypoints, do not call entry points from other erp methods, consider extracting a helper instead
- The `www_entry_point`:
    - Sets up a savepoint (subtransaction), that will be rolled back in case an exception is raised
    - Turns exceptions into json dictionaries
    - Receives a list of expected exceptions. For those:
        - They should have a `to_dict()` method that returns all fields but the traceback
        - The exception class name will be set as `code` attribute
        - The remote (erp) traceback will be added
    - Any unexpected exception
        - code: 'Unexpected'
        - error: `str(e)`
        - also the traceback
- **Important:** Let exceptions reach the decorator to get a full report in the API
- In order to simplify response handling in clients:
    - Always the response is a dictionary (avoid strings or lists on first level)
    - If the dictionary has an error attribute it is an error and the attribute is an english description of the error.
    - `code` can be use to identify the case.
- Still errors can happen outside the wrapper
    - Network errors: restfull gives HTTP errors
    - Errors locating the entry point (bad model, bad model method) gives a 210 HTTP error.

## API-ERP interface

Low level erp api access:

- Detects any ConnectionError which is raised as ErpConnectionError, generating a GATEWAY ERROR
- Any 4xx or 5xx errors will be raised as httpx `raise_on_status`
- Any json encoding problems will be raised as well
- HTTP 210 which corresponds to errors while accessing the entry point are reported as  `ErpUnexpectedError`
- Expected and unexpected erp errors are HTTP 200 and are handled in the next level

ERP data source process expected ERP exceptions and erp returned data validation exceptions

- Expected ERP exceptions classes are replicated in api level (Match names)
- From a list of expected exceptions we 
- Their base class, ErpError, process includes in the error description the code, the error (message) and the remote backtrace.
- After each erp call we call `processErpErrors` which detects error dictionaries and raises the proper exception
- In case 

TODO: move `process_erp_errors` to the low level vGiven that the error processing is that uniform maybe we could join at least the `process_erp_errors` part

ERP validation errors



## Instal·lations





- ERP down:
    - api: envia un HTTP: GATEWAY_ERROR
    - ui: Ara mateix els nostres sistemes no estan disponibles
- Unexpected ERP
    - api: 500, envia al sentry/log, generar error id 
    - ui: S'ha produit un error inexperat. Contacta amb nosaltres. La referencia de l'error es XXXX.
    - Include errors before getting into the context handler (ie. locating the class or the method, or calling it with the proper arguments)
- Expected:
    - User not found
        - api: 500, envia al sentry/log, generar error id 
        - ui: S'ha produit un error inexperat. Contacta amb nosaltres. La referencia de l'error es XXXX.
    - Installations not found
        - api: retorna []
        - ui: gestiona la [] poniendo un mensaje en la tabla
- API down (o internet down)
    - ui: No es pot accedir al servidor, comprova la teva conexió a internet
- API version missmatch:
    - ui: Automatic reload in N seconds
- API unexpected error:
    - api: 500, log/sentry, generar id
    - ui: S'ha produit un error inexperat. Contacta amb nosaltres. La referencia de l'error es XXXX.
- API input validation error: Error de programacion ui
    - api: rely on fastapi errors
    - ui: Se ha producido un error inexperado
    - TODO: Como recoger info de lo que ha pasado
- API 404: Error de programacion ui
    - api: rely on fastapi errors
    - ui: Error de programacion ui
    - TODO: Como recoger info de lo que ha pasado
- API authentication error: Using a protected entry points (requires any user)
- API unauthorized error: Using restricted entry points (requires a concrete user or role)



- Si no hi ha errors retorna el resultat
- Si hi ha un error, la funcio d'ovapi llença (throw) un missatge traduit.
    - Si l'error es un dels comuns, (Network error, Gateway error, Unexpected API error, Unexpected ERP error) ho gestion commonErrors, cridant al messages service (snackbar) i retornant l'string de l'error
    - Si es un error esperat propi del punt d'entrada, Login amb password no validad, el handler especific ha de gestionar l'error. Perque aixo pasi el commonErrors ha de llençar-ho i la funció de ovapi ha de agafar-ho i extreure el missatge d'error.
