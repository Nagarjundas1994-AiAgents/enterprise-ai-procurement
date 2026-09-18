import "./globals.css";

export const metadata = {
  title: "ProcureChat — AI Procurement Assistant",
  description: "Requisitions, orders, suppliers and a DeepSeek AI assistant."
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
