'use client';
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = Home;
const lucide_react_1 = require("lucide-react");
const stats = [
    {
        name: 'Totale Omzet',
        value: '€54,763',
        icon: lucide_react_1.DollarSign,
        change: '+12.5%',
        changeType: 'positive'
    },
    {
        name: 'Nieuwe Klanten',
        value: '2,345',
        icon: lucide_react_1.Users,
        change: '+18.2%',
        changeType: 'positive'
    },
    {
        name: 'Orders',
        value: '12,543',
        icon: lucide_react_1.Package,
        change: '-2.3%',
        changeType: 'negative'
    },
    {
        name: 'Gemiddelde Order',
        value: '€247',
        icon: lucide_react_1.BarChart3,
        change: '+4.1%',
        changeType: 'positive'
    }
];
function Home() {
    return (<div className="p-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (<div key={stat.name} className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-full ${stat.changeType === 'positive' ? 'bg-green-100' : 'bg-red-100'}`}>
                <stat.icon className={`w-6 h-6 ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}/>
              </div>
            </div>
            
            <div className="mt-4">
              <span className={`text-sm font-medium ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
                {stat.change}
              </span>
              <span className="text-sm text-gray-500 ml-2">vs vorige maand</span>
            </div>
          </div>))}
      </div>
    </div>);
}
//# sourceMappingURL=page.js.map