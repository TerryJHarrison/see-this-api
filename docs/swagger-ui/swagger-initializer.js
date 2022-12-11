window.onload = function() {
    //<editor-fold desc="Changeable Configuration Block">

    // Set path to swagger file base off environment
    // TODO: more elegant solution
    const isLocal = false;
    const url = isLocal ? "/swagger.json" : "/see-this-api/swagger.json";

    // the following lines will be replaced by docker/configurator, when it runs in a docker-container
    window.ui = SwaggerUIBundle({
        url: url,
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
        ],
        plugins: [
            SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout"
    });

    //</editor-fold>
};