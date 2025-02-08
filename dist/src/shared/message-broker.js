"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MessageBroker = void 0;
const amqplib_1 = require("amqplib");
class MessageBroker {
    async connect() {
        this.connection = await amqplib_1.default.connect(process.env.RABBITMQ_URL);
        this.channel = await this.connection.createChannel();
    }
    async publishEvent(exchange, routingKey, data) {
        await this.channel.publish(exchange, routingKey, Buffer.from(JSON.stringify(data)), { persistent: true });
    }
}
exports.MessageBroker = MessageBroker;
//# sourceMappingURL=message-broker.js.map