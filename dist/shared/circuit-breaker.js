"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createCircuitBreaker = createCircuitBreaker;
const opossum_1 = require("opossum");
function createCircuitBreaker(asyncFn) {
    return new opossum_1.CircuitBreaker(asyncFn, {
        timeout: 3000,
        errorThresholdPercentage: 50,
        resetTimeout: 30000
    });
}
//# sourceMappingURL=circuit-breaker.js.map