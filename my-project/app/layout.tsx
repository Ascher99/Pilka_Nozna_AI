import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pl">
      <body className="bg-gray-900 text-blue-200 min-h-screen">
        <main className="max-w-5xl mx-auto p-6">{children}</main>
      </body>
    </html>
  );
}
