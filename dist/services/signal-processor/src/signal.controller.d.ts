export declare class SignalController {
    private messageBroker;
    constructor();
    handleSignal(data: any): Promise<void>;
    private processSignal;
}
