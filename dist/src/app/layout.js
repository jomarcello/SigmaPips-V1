'use client';
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = RootLayout;
const google_1 = require("next/font/google");
const Sidebar_1 = require("@/components/layout/Sidebar");
const Header_1 = require("@/components/layout/Header");
const utils_1 = require("@/lib/utils");
require("./globals.css");
const inter = (0, google_1.Inter)({ subsets: ['latin'] });
function RootLayout({ children, }) {
    return (<html lang="nl">
      <body className={(0, utils_1.cn)(inter.className, "bg-gray-50")}>
        <div className="flex h-screen">
          <Sidebar_1.default />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header_1.default />
            <main className="flex-1 overflow-y-auto p-4">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>);
}
//# sourceMappingURL=layout.js.map