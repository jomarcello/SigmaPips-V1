"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.serviceConfigs = void 0;
exports.serviceConfigs = [
    {
        name: 'Signal Entry & News Scraper',
        githubRepo: 'tradingview-signal-processor',
        railwayUrl: 'https://tradingview-signal-processor-production.up.railway.app',
        expectedEndpoints: ['/webhook', '/health']
    },
    {
        name: 'AI Signal Processor',
        githubRepo: 'tradingview-signal-ai-service',
        railwayUrl: 'https://tradingview-signal-ai-service-production.up.railway.app',
        expectedEndpoints: ['/process-signal', '/health']
    },
];
//# sourceMappingURL=config.js.map