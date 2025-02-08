"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const testing_1 = require("@nestjs/testing");
const signal_controller_1 = require("../src/signal.controller");
describe('SignalController', () => {
    let controller;
    beforeEach(async () => {
        const module = await testing_1.Test.createTestingModule({
            controllers: [signal_controller_1.SignalController],
        }).compile();
        controller = module.get(signal_controller_1.SignalController);
    });
    it('should process signals correctly', async () => {
    });
});
//# sourceMappingURL=signal.controller.spec.js.map