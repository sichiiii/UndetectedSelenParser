function startProxy() {
        var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: 	"IP",		// Proxy IP or URL: type -> string
                port: 	PORT		// Proxy port : type -> int
            },
            bypassList: ["localhost"]
            }
        };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        }

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "username",   // Enter your username
                    password: "password"   // Enter your password
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        startProxy();
                
