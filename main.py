import os
import sys
import random
import json
from pathlib import Path
from datetime import datetime
import time

import webview
from colorama import init as colorama_init, Fore, Style

REMOTE_URL = 'https://web.max.ru'
USERAGENTS_PATH = os.path.join('data', 'useragents.txt')
ICON_PNG_PATH = os.path.join('assets', 'icon.png')
ICON_ICO_PATH = os.path.join('assets', 'icon.ico')
WINDOW_TITLE = 'YeMax'
WIDTH = 1200
HEIGHT = 800
HTTP_PORT = 13377

colorama_init()

class Logger:
    def _fmt(self, color, tag, message):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{color}[{ts}] [{tag}] {message}{Style.RESET_ALL}")
    def info(self, msg): self._fmt(Fore.CYAN, 'INFO', msg)
    def ok(self, msg): self._fmt(Fore.GREEN, 'OK', msg)
    def warn(self, msg): self._fmt(Fore.YELLOW, 'WARN', msg)
    def error(self, msg): self._fmt(Fore.RED, 'ERROR', msg)
    def priv(self, msg): self._fmt(Fore.MAGENTA, 'PRIV', msg)
    def dbg(self, msg): self._fmt(Fore.BLUE, 'DEBUG', msg)

log = Logger()

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/130.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/129.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/128.0.0.0',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
]

FALLBACK_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'


def pick_ua(agents):
    ua = random.choice(agents)
    log.info(f'User-Agent selected: {ua}')
    return ua

BLOCKED_DOMAINS = [
    'google-analytics','analytics','yandex','mixpanel','amplitude','hotjar','doubleclick',
    'googletagmanager','gtag','facebook','segment','matomo','ads','adsystem'
]

INJECT_JS = r"""
(function(){
    function safeCall(name){
        try{ if(window.pywebview && window.pywebview.api && window.pywebview.api.reportDisabled) window.pywebview.api.reportDisabled(name) }catch(e){}
    }
    try{
        if('geolocation' in navigator){
            navigator.geolocation.getCurrentPosition = function(success, error){
                if(error) error({code:1,message:'Permission denied by app injection'});
                safeCall('geolocation:getCurrentPosition_overridden');
            };
            navigator.geolocation.watchPosition = function(){ safeCall('geolocation:watchPosition_overridden'); return null; };
            safeCall('geolocation:overrides_applied');
        } else { safeCall('geolocation:not_present'); }
    }catch(e){ safeCall('geolocation:error'); }
    try{
        if(navigator.sendBeacon){
            navigator.sendBeacon = function(){ safeCall('sendBeacon:overridden'); return false; };
            safeCall('sendBeacon:overrides_applied');
        } else { safeCall('sendBeacon:not_present'); }
    }catch(e){ safeCall('sendBeacon:error'); }
    try{
        if(navigator.serviceWorker && navigator.serviceWorker.register){
            navigator.serviceWorker.register = function(){ safeCall('serviceWorker:register_blocked'); return Promise.reject(new Error('Service workers disabled by app')); };
            safeCall('serviceWorker:overrides_applied');
        } else { safeCall('serviceWorker:not_present'); }
    }catch(e){ safeCall('serviceWorker:error'); }
    try{
        if(navigator.connection){
            try{ delete navigator.connection; safeCall('network_info:deleted'); }catch(e){ navigator.connection = undefined; safeCall('network_info:unset_failed'); }
        } else { safeCall('network_info:not_present'); }
    }catch(e){ safeCall('network_info:error'); }
    (function(){
        var blocked = %s;
        var origFetch = window.fetch;
        window.fetch = function(input, init){
            try{
                var url = (typeof input === 'string') ? input : (input && input.url) || '';
                for(var i=0;i<blocked.length;i++){
                    if(url.indexOf(blocked[i]) !== -1){
                        safeCall('fetch:block:' + blocked[i] + ':' + url);
                        return origFetch.apply(this, arguments);
                    }
                }
            }catch(e){}
            return origFetch.apply(this, arguments);
        };
        var XOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url){
            try{
                for(var j=0;j<blocked.length;j++){
                    if(typeof url === 'string' && url.indexOf(blocked[j])!==-1){
                        safeCall('xhr:block:' + blocked[j] + ':' + url);
                    }
                }
            }catch(e){}
            return XOpen.apply(this, arguments);
        };
        safeCall('network:blockers:installed');
    })();
    (function(){
        var blocked = %s;
        var observer = new MutationObserver(function(mutations){
            mutations.forEach(function(m){
                if(m.addedNodes && m.addedNodes.length){
                    m.addedNodes.forEach(function(node){
                        try{
                            if(node.tagName === 'SCRIPT' && node.src){
                                for(var i=0;i<blocked.length;i++){
                                    if(node.src.indexOf(blocked[i]) !== -1){
                                        var s = node.src;
                                        node.type = 'javascript/blocked';
                                        if(node.parentNode) node.parentNode.removeChild(node);
                                        safeCall('script:block:' + blocked[i] + ':' + s);
                                    }
                                }
                            }
                        }catch(e){}
                    });
                }
            });
        });
        observer.observe(document.documentElement || document, { childList:true, subtree:true });
        safeCall('dom:observer_installed');
    })();
    function replaceTextContent(rootNode) {
        var walk = document.createTreeWalker(
            rootNode,
            NodeFilter.SHOW_TEXT,
            null
        );
        var node;
        while (node = walk.nextNode()) {
            if (node.nodeValue.indexOf('MAX') !== -1) {
                node.nodeValue = node.nodeValue.replace(/MAX/g, 'YeMax');
            }
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            replaceTextContent(document.body);
        });
    } else {
        replaceTextContent(document.body);
    }
    safeCall('injection:complete');
})();
""" % (json.dumps(BLOCKED_DOMAINS), json.dumps(BLOCKED_DOMAINS))


main_window = None

class Api:
    def reportDisabled(self, name):
        try:
            log.priv(f'JS -> disabled/blocked: {name}')
        except:
            pass
    def clearCookies(self):
        try:
            if main_window:
                main_window.clear_cookies()
                log.warn('Cookies cleared via API (main_window.clear_cookies())')
                return True
        except Exception as e:
            log.error(f'Error in clearCookies: {e}')
        return False
    def listCookies(self):
        try:
            if main_window:
                cookies = main_window.get_cookies()
                out = []
                for c in cookies:
                    try:
                        name = getattr(c, 'name', getattr(c, 'key', 'unknown'))
                        domain = getattr(c, 'domain', getattr(c, 'domain_specified', ''))
                        path = getattr(c, 'path', '/')
                        secure = getattr(c, 'secure', False)
                        expires = getattr(c, 'expires', None)
                        out.append({'name':name,'domain':domain,'path':path,'secure':secure,'expires':expires})
                    except:
                        pass
                log.dbg(f'listCookies returned {len(out)} items')
                return out
        except Exception as e:
            log.error(f'Error in listCookies: {e}')
        return []

def on_loaded(window):
    try:
        log.info('Loaded event — JS injection started')
        window.evaluate_js(INJECT_JS)
        log.ok('JS injection sent to content (evaluate_js)')
    except Exception as e:
        log.error(f'Error during JS injection: {e}')

def on_shown(window):
    log.ok('Window shown to user')

def on_error(window, exc):
    log.error(f'Webview exception: {exc}')

def main():
    agents = USER_AGENTS
    if not agents:
        agents = [FALLBACK_UA]
    ua = pick_ua(agents)
    api = Api()
    global main_window

    if os.path.exists(ICON_ICO_PATH):
        icon_arg = ICON_ICO_PATH
    elif os.path.exists(ICON_PNG_PATH):
        icon_arg = ICON_PNG_PATH
    else:
        icon_arg = None

    main_window = webview.create_window(
        WINDOW_TITLE,
        REMOTE_URL,
        js_api=api,
        width=WIDTH,
        height=HEIGHT,
        confirm_close=False,
        text_select=True,
        minimized=True,
        maximized=False,
    )

    main_window.events.loaded += on_loaded
    main_window.events.shown += on_shown
    webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    webview.settings['ALLOW_DOWNLOADS'] = True
    
    try:
        log.info(f'Starting webview: http_server=True, private_mode=False, http_port={HTTP_PORT}, ssl=True (direct connection)')
        webview.start(http_server=True, http_port=HTTP_PORT, private_mode=False, ssl=True, gui=None, debug=False, user_agent=ua)
    except Exception as e:
        log.error(f'Failed to start webview: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
