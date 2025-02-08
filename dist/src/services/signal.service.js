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
exports.SignalService = void 0;
const common_1 = require("@nestjs/common");
const message_broker_1 = require("../shared/message-broker");
let SignalService = class SignalService {
    constructor() {
        this.messageBroker = new message_broker_1.MessageBroker();
        this.messageBroker.connect();
    }
    async processSignal(data) {
        const processedData = Object.assign(Object.assign({}, data), { processed: true, timestamp: new Date() });
        await this.messageBroker.publishEvent('signals', 'signal.processed', processedData);
        return processedData;
    }
};
exports.SignalService = SignalService;
exports.SignalService = SignalService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [])
], SignalService);
//# sourceMappingURL=signal.service.js.map