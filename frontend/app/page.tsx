export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-4">
          🎯 Sales AI Dojo
        </h1>
        <p className="text-center text-xl mb-8">
          Plataforma de treinamento de vendedores com IA de voz
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Para Vendedores</h2>
            <p className="text-muted-foreground mb-4">
              Pratique conversas de vendas com clientes simulados por IA e receba feedback instantâneo.
            </p>
            <a
              href="/login"
              className="inline-block bg-primary text-primary-foreground px-6 py-2 rounded-md hover:opacity-90 transition"
            >
              Começar Treino
            </a>
          </div>

          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Para Gestores</h2>
            <p className="text-muted-foreground mb-4">
              Acompanhe o desempenho da equipe e identifique oportunidades de melhoria.
            </p>
            <a
              href="/login"
              className="inline-block bg-secondary text-secondary-foreground px-6 py-2 rounded-md hover:opacity-90 transition"
            >
              Ver Dashboard
            </a>
          </div>
        </div>

        <div className="mt-16 text-center">
          <h3 className="text-xl font-semibold mb-4">Como Funciona</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
            <div className="text-center">
              <div className="text-4xl mb-2">📄</div>
              <p className="font-medium">1. Onboarding</p>
              <p className="text-sm text-muted-foreground">Upload de documentos</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">🤖</div>
              <p className="font-medium">2. IA gera personas</p>
              <p className="text-sm text-muted-foreground">Clientes realistas</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">🎤</div>
              <p className="font-medium">3. Simulação de voz</p>
              <p className="text-sm text-muted-foreground">Conversa em tempo real</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">📊</div>
              <p className="font-medium">4. Feedback IA</p>
              <p className="text-sm text-muted-foreground">Análise e insights</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
