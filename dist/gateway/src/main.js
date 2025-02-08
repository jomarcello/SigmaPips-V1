"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@nestjs/core");
const app_module_1 = require("./app.module");
const express_rate_limit_1 = require("express-rate-limit");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule);
    app.use((0, express_rate_limit_1.rateLimit)({
        windowMs: 15 * 60 * 1000,
        max: 100
    }));
    await app.listen(3000);
}
bootstrap();
//# sourceMappingURL=main.js.map