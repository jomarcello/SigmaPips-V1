"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SignalController = void 0;
const common_1 = require("@nestjs/common");
const microservices_1 = require("@nestjs/microservices");
const message_broker_1 = require("../../../shared/message-broker");
let SignalController = class SignalController {
    constructor() {
        this.messageBroker = new message_broker_1.MessageBroker();
        this.messageBroker.connect();
    }
    async handleSignal(data) {
        try {
            const processedSignal = await this.processSignal(data);
            await this.messageBroker.publishEvent('signals', 'signal.processed', processedSignal);
        }
        catch (error) {
            console.error('Error processing signal:', error);
        }
    }
    async processSignal(data) {
        return data;
    }
};
exports.SignalController = SignalController;
__decorate([
    (0, microservices_1.EventPattern)('trading.signal'),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], SignalController.prototype, "handleSignal", null);
exports.SignalController = SignalController = __decorate([
    (0, common_1.Controller)(),
    __metadata("design:paramtypes", [])
], SignalController);
//# sourceMappingURL=signal.controller.js.map