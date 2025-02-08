export declare class MessageBroker {
    private connection;
    private channel;
    connect(): Promise<void>;
    publishEvent(exchange: string, routingKey: string, data: any): Promise<void>;
}
