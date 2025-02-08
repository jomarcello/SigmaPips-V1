"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const http_proxy_middleware_1 = require("http-proxy-middleware");
const app = (0, express_1.default)();
app.use(rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100
}));
app.use('/signals', (0, http_proxy_middleware_1.createProxyMiddleware)({
    target: 'http://signal-processor:3000',
    changeOrigin: true
}));
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy' });
});
//# sourceMappingURL=api-gateway.js.map