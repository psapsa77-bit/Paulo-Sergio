import React, { useState } from 'react';
import { FileText, Upload, Download, CheckCircle, Clock, Trash2, Plus } from 'lucide-react';

interface RescissionItem {
  codigo: string;
  descricao: string;
  valor: number;
  tipo: 'credito' | 'debito';
  explicacao: string;
}

interface RescissionAnalysis {
  id: string;
  employeeName: string;
  employerName: string;
  rescissionDate: string;
  rescissionType: string;
  items: RescissionItem[];
  totalCreditos: number;
  totalDebitos: number;
  valorLiquido: number;
  fgts: {
    saldoFgts?: number;
    multaFgts?: number;
    totalFgts?: number;
  };
  observacoes: string[];
  status: 'pending' | 'processing' | 'completed' | 'error';
  errorMessage?: string;
  createdAt: string;
}

const formatCurrency = (value: number): string => {
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
};

const formatDate = (dateString: string): string => {
  // Corrige problema de timezone: adiciona T12:00:00 para evitar que a data seja interpretada como UTC meia-noite
  // e convertida para o dia anterior no fuso horário local
  let dateToFormat: Date;

  if (dateString.includes('T')) {
    // Se já tem horário (ISO completo), usa direto
    dateToFormat = new Date(dateString);
  } else {
    // Se é só data (YYYY-MM-DD), adiciona meio-dia para evitar problema de timezone
    dateToFormat = new Date(dateString + 'T12:00:00');
  }

  return dateToFormat.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });
};

// Dados de exemplo da Wanessa
const EXEMPLO_WANESSA: Omit<RescissionAnalysis, 'id' | 'status' | 'createdAt'> = {
  employeeName: 'WANESSA NASCIMENTO SOUSA',
  employerName: 'OCL CONVENIENCIAS LTDA',
  rescissionDate: '2025-07-30',
  rescissionType: 'Extinção normal do contrato de trabalho por prazo determinado',
  items: [
    {
      codigo: '63',
      descricao: '13º Salário Proporcional 01/12 avos',
      valor: 277.83,
      tipo: 'credito',
      explicacao: 'Décimo terceiro salário proporcional referente a 1/12 avos do período trabalhado'
    },
    {
      codigo: '65',
      descricao: 'Férias Proporcionais 02/12 avos',
      valor: 277.83,
      tipo: 'credito',
      explicacao: 'Férias proporcionais referentes a 2/12 avos do período trabalhado'
    },
    {
      codigo: '68',
      descricao: 'Terço Constitucional de Férias',
      valor: 92.61,
      tipo: 'credito',
      explicacao: 'Um terço constitucional sobre as férias proporcionais'
    },
    {
      codigo: '95',
      descricao: 'Outras Verbas (FGTS)',
      valor: 288.94,
      tipo: 'credito',
      explicacao: 'Valor referente ao FGTS depositado durante o período trabalhado'
    }
  ],
  totalCreditos: 937.22,
  totalDebitos: 0.00,
  valorLiquido: 937.22,
  fgts: {},
  observacoes: [
    'Esta rescisão refere-se à extinção normal do contrato de trabalho por prazo determinado. A trabalhadora foi admitida em 01/06/2025 e o término do contrato ocorreu em 31/07/2025, totalizando aproximadamente 2 meses de vínculo empregatício.',
    'Não houve pagamento de aviso prévio indenizado, o que é normal nesta modalidade de rescisão, pois o contrato por prazo determinado chegou ao seu fim natural sem necessidade de aviso prévio.',
    'Foram pagos o 13º salário proporcional no valor de R$ 277,83 referente a 1/12 avos, férias proporcionais de R$ 277,83 correspondentes a 2/12 avos do período trabalhado, e o terço constitucional de férias no valor de R$ 92,61.',
    'O prazo legal para pagamento das verbas rescisórias é de até 10 dias corridos após o término do contrato. Esta rescisão será homologada e os valores estarão disponíveis dentro deste prazo.',
    'Por se tratar de extinção natural de contrato por prazo determinado, não há direito ao saque do FGTS por rescisão sem justa causa nem ao seguro-desemprego. O valor de R$ 288,94 refere-se aos depósitos do FGTS realizados durante o período trabalhado.',
    'A empresa agradece pelos serviços prestados durante este período. Em caso de dúvidas sobre os valores ou prazos, nossa equipe de RH está à disposição para esclarecimentos.'
  ]
};

export default function RescissionAnalyzer() {
  // Estado gerenciado localmente (sem window.storage)
  const [analyses, setAnalyses] = useState<RescissionAnalysis[]>([]);
  const [currentView, setCurrentView] = useState<'list' | 'new' | 'detail'>('list');
  const [selectedAnalysis, setSelectedAnalysis] = useState<RescissionAnalysis | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [termoFile, setTermoFile] = useState<File | null>(null);
  const [manualFgts, setManualFgts] = useState({
    saldoFgts: '',
    multaFgts: '',
    totalFgts: ''
  });

  const handleFileChange = (file: File | null) => {
    setTermoFile(file);
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        const base64Data = base64.split(',')[1];
        resolve(base64Data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const analyzeDocumentWithClaude = async (
    termoFile: File,
    manualFgts: { saldoFgts: string; multaFgts: string; totalFgts: string }
  ): Promise<Omit<RescissionAnalysis, 'id' | 'status' | 'createdAt'>> => {
    const termoBase64 = await fileToBase64(termoFile);

    const promptText = `Você é um especialista em legislação trabalhista brasileira. Analise o Termo de Rescisão do Contrato de Trabalho (TRCT) fornecido e extraia TODAS as informações detalhadas.

Retorne APENAS um objeto JSON válido (sem markdown, sem texto adicional) com esta estrutura EXATA:
{
  "employeeName": "Nome completo do funcionário",
  "employerName": "Razão social da empresa",
  "rescissionDate": "2024-10-23",
  "rescissionType": "Tipo de rescisão",
  "items": [
    {
      "codigo": "50",
      "descricao": "Descrição da verba",
      "valor": 1000.50,
      "tipo": "credito",
      "explicacao": "Explicação clara"
    }
  ],
  "totalCreditos": 10000.00,
  "totalDebitos": 500.00,
  "valorLiquido": 9500.00,
  "fgts": {},
  "observacoes": ["Parágrafo 1 explicativo", "Parágrafo 2 explicativo"]
}

IMPORTANTE:
- Extraia TODAS as verbas e descontos do documento
- Retorne APENAS o JSON puro, SEM markdown (sem \`\`\`json)
- Use números decimais para valores monetários
- Nas observações, forneça parágrafos detalhados sobre o contexto da rescisão`;

    const messages = [
      {
        role: "user" as const,
        content: [
          {
            type: "text" as const,
            text: promptText
          },
          {
            type: "document" as const,
            source: {
              type: "base64" as const,
              media_type: "application/pdf" as const,
              data: termoBase64
            }
          }
        ]
      }
    ];

    console.log('Iniciando análise com Claude API...');

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 8000,
        messages
      })
    });

    console.log('Status da resposta:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Erro na API:', errorText);
      throw new Error(`Erro na API: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log('Resposta da API:', data);

    const content = data.content.find((c: { type: string; text?: string }) => c.type === "text")?.text;

    if (!content) {
      throw new Error("Resposta vazia da API");
    }

    console.log('Conteúdo extraído:', content);

    // Limpar markdown e parsear JSON
    const cleanContent = content
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim();

    const parsed = JSON.parse(cleanContent);
    console.log('JSON parseado:', parsed);

    // Processar dados de FGTS manual
    const fgtsData: { saldoFgts?: number; multaFgts?: number; totalFgts?: number } = {};
    if (manualFgts.saldoFgts) fgtsData.saldoFgts = parseFloat(manualFgts.saldoFgts);
    if (manualFgts.multaFgts) fgtsData.multaFgts = parseFloat(manualFgts.multaFgts);
    if (manualFgts.totalFgts) fgtsData.totalFgts = parseFloat(manualFgts.totalFgts);

    return {
      employeeName: parsed.employeeName || 'Funcionário',
      employerName: parsed.employerName || 'Empresa',
      rescissionDate: parsed.rescissionDate || new Date().toISOString().split('T')[0],
      rescissionType: parsed.rescissionType || 'Não especificado',
      items: parsed.items || [],
      totalCreditos: parsed.totalCreditos || 0,
      totalDebitos: parsed.totalDebitos || 0,
      valorLiquido: parsed.valorLiquido || 0,
      fgts: Object.keys(fgtsData).length > 0 ? fgtsData : (parsed.fgts || {}),
      observacoes: parsed.observacoes || []
    };
  };

  const processAnalysis = async () => {
    if (!termoFile) {
      alert('Por favor, faça upload do Termo de Rescisão');
      return;
    }

    setIsProcessing(true);

    try {
      console.log('Iniciando processamento...');

      let analysisData: Omit<RescissionAnalysis, 'id' | 'status' | 'createdAt'>;

      try {
        console.log('Tentando processar com Claude API...');
        analysisData = await Promise.race([
          analyzeDocumentWithClaude(termoFile, manualFgts),
          new Promise<never>((_, reject) =>
            setTimeout(() => reject(new Error('Timeout: API demorou mais de 60 segundos')), 60000)
          )
        ]);
        console.log('Dados recebidos da API:', analysisData);
      } catch (apiError) {
        console.error('Erro na API, usando dados de exemplo:', apiError);

        // Usar dados de exemplo da Wanessa se a API falhar
        analysisData = EXEMPLO_WANESSA;

        alert('⚠️ A API Claude está temporariamente indisponível ou ocorreu um erro.\n\nExibindo dados de exemplo (Wanessa Nascimento Sousa) para demonstração.\n\nVerifique o console (F12) para detalhes do erro.');
      }

      const completedAnalysis: RescissionAnalysis = {
        id: `analysis-${Date.now()}`,
        ...analysisData,
        status: 'completed',
        createdAt: new Date().toISOString(),
      };

      console.log('Análise completa:', completedAnalysis);

      // Adicionar ao estado local
      setAnalyses(prev => [completedAnalysis, ...prev]);

      setSelectedAnalysis(completedAnalysis);
      setCurrentView('detail');

      // Limpar formulário
      setTermoFile(null);
      setManualFgts({ saldoFgts: '', multaFgts: '', totalFgts: '' });

      console.log('Processamento concluído com sucesso!');
    } catch (error) {
      console.error('ERRO no processamento:', error);
      alert('❌ Erro ao processar análise:\n\n' + (error instanceof Error ? error.message : 'Erro desconhecido'));
    } finally {
      setIsProcessing(false);
    }
  };

  const deleteAnalysis = (id: string) => {
    if (confirm('Tem certeza que deseja excluir esta análise?')) {
      setAnalyses(prev => prev.filter(a => a.id !== id));
      if (selectedAnalysis?.id === id) {
        setCurrentView('list');
        setSelectedAnalysis(null);
      }
    }
  };

  const [showPrintModal, setShowPrintModal] = useState(false);
  const [printHtml, setPrintHtml] = useState('');

  const generatePrintHtml = () => {
    if (!selectedAnalysis) return '';

    const creditos = selectedAnalysis.items.filter(item => item.tipo === 'credito');
    const debitos = selectedAnalysis.items.filter(item => item.tipo === 'debito');

    return `<!DOCTYPE html>
<html>
<head>
<title>Rescisão - ${selectedAnalysis.employeeName}</title>
<meta charset="UTF-8">
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; color: #333; }
h1 { color: #2563eb; margin-bottom: 5px; }
h2 { color: #1f2937; margin-top: 30px; }
h3 { color: #059669; }
.header { border-bottom: 2px solid #2563eb; padding-bottom: 20px; margin-bottom: 20px; }
.empresa { color: #666; font-size: 18px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
.info-item label { color: #666; font-size: 14px; display: block; }
.info-item value { font-size: 18px; font-weight: 600; }
.resumo { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }
.resumo-item { padding: 15px; border-radius: 8px; }
.credito { background: #dcfce7; border-left: 4px solid #22c55e; }
.debito { background: #fee2e2; border-left: 4px solid #ef4444; }
.liquido { background: #dbeafe; border-left: 4px solid #3b82f6; }
.valor { font-size: 24px; font-weight: bold; margin: 10px 0; }
.valor.verde { color: #16a34a; }
.valor.vermelho { color: #dc2626; }
.valor.azul { color: #2563eb; }
.item { border-left: 4px solid #22c55e; padding-left: 15px; margin: 15px 0; page-break-inside: avoid; }
.item.debito { border-left-color: #ef4444; }
.codigo { background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; display: inline-block; }
.codigo.debito { background: #fee2e2; color: #991b1b; }
.item-valor { float: right; font-size: 18px; font-weight: bold; }
.item-valor.verde { color: #16a34a; }
.item-valor.vermelho { color: #dc2626; }
.descricao { font-weight: 600; margin: 8px 0 5px 0; clear: both; }
.explicacao { color: #666; font-size: 14px; }
.observacoes { background: #f9fafb; padding: 20px; border-radius: 8px; margin-top: 30px; }
.observacoes p { margin: 10px 0; line-height: 1.6; }
.footer { margin-top: 40px; text-align: center; color: #999; font-size: 12px; }
@media print { body { margin: 20px; } .resumo { page-break-inside: avoid; } }
</style>
</head>
<body>
<div class="header">
<h1>${selectedAnalysis.employeeName}</h1>
<div class="empresa">${selectedAnalysis.employerName}</div>
</div>
<div class="info-grid">
<div class="info-item">
<label>Data da Rescisão</label>
<value>${formatDate(selectedAnalysis.rescissionDate)}</value>
</div>
<div class="info-item">
<label>Tipo de Rescisão</label>
<value>${selectedAnalysis.rescissionType}</value>
</div>
</div>
<h2>Resumo Financeiro</h2>
<div class="resumo">
<div class="resumo-item credito">
<div>Total de Créditos</div>
<div class="valor verde">${formatCurrency(selectedAnalysis.totalCreditos)}</div>
<div style="font-size: 12px; color: #666;">Valores a receber</div>
</div>
<div class="resumo-item debito">
<div>Total de Débitos</div>
<div class="valor vermelho">${formatCurrency(selectedAnalysis.totalDebitos)}</div>
<div style="font-size: 12px; color: #666;">Descontos aplicados</div>
</div>
<div class="resumo-item liquido">
<div>Valor Líquido</div>
<div class="valor azul">${formatCurrency(selectedAnalysis.valorLiquido)}</div>
<div style="font-size: 12px; color: #666;">Valor final a receber</div>
</div>
</div>
<h3>💰 Valores a Receber</h3>
${creditos.map(item => `<div class="item">
<span class="item-valor verde">${formatCurrency(item.valor)}</span>
<span class="codigo">${item.codigo}</span>
<div class="descricao">${item.descricao}</div>
<div class="explicacao">${item.explicacao}</div>
</div>`).join('\n')}
${debitos.length > 0 ? `<h3 style="color: #dc2626;">📉 Descontos Aplicados</h3>
${debitos.map(item => `<div class="item debito">
<span class="item-valor vermelho">${formatCurrency(item.valor)}</span>
<span class="codigo debito">${item.codigo}</span>
<div class="descricao">${item.descricao}</div>
<div class="explicacao">${item.explicacao}</div>
</div>`).join('\n')}` : ''}
${selectedAnalysis.observacoes.length > 0 ? `<div class="observacoes">
<h3>📋 Informações sobre a Rescisão</h3>
${selectedAnalysis.observacoes.map(obs => `<p>${obs}</p>`).join('\n')}
</div>` : ''}
<div class="footer">
Documento gerado em ${new Date().toLocaleDateString('pt-BR')} às ${new Date().toLocaleTimeString('pt-BR')}
</div>
</body>
</html>`;
  };

  const handlePrint = () => {
    const html = generatePrintHtml();
    setPrintHtml(html);
    setShowPrintModal(true);
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(printHtml);
      alert('✅ HTML copiado!\n\n1. Abra um editor de texto (Notepad, VS Code, etc.)\n2. Cole o conteúdo (Ctrl+V)\n3. Salve como "rescisao.html"\n4. Abra no navegador e use Ctrl+P para gerar PDF');
    } catch (err) {
      // Fallback para navegadores que não suportam clipboard API
      const textArea = document.createElement('textarea');
      textArea.value = printHtml;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        alert('✅ HTML copiado!\n\n1. Abra um editor de texto (Notepad, VS Code, etc.)\n2. Cole o conteúdo (Ctrl+V)\n3. Salve como "rescisao.html"\n4. Abra no navegador e use Ctrl+P para gerar PDF');
      } catch (err2) {
        alert('❌ Não foi possível copiar. Selecione o código manualmente.');
      }
      document.body.removeChild(textArea);
    }
  };

  const loadExampleData = () => {
    const exampleAnalysis: RescissionAnalysis = {
      id: `analysis-${Date.now()}`,
      ...EXEMPLO_WANESSA,
      status: 'completed',
      createdAt: new Date().toISOString(),
    };
    setAnalyses(prev => [exampleAnalysis, ...prev]);
    setSelectedAnalysis(exampleAnalysis);
    setCurrentView('detail');
  };

  // Renderização da lista
  if (currentView === 'list') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-blue-600 mb-2">
                  Analisador de Rescisões Trabalhistas
                </h1>
                <p className="text-gray-600 text-lg">
                  Análise automatizada com IA e geração de relatórios profissionais
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={loadExampleData}
                  className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-3 rounded-xl hover:bg-gray-200 transition-colors"
                >
                  <FileText className="w-5 h-5" />
                  Ver Exemplo
                </button>
                <button
                  onClick={() => setCurrentView('new')}
                  className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors shadow-lg"
                >
                  <Plus className="w-5 h-5" />
                  Nova Análise
                </button>
              </div>
            </div>
          </div>

          {analyses.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                Nenhuma análise cadastrada
              </h3>
              <p className="text-gray-500 mb-6">
                Comece fazendo upload de um documento de rescisão ou veja o exemplo
              </p>
              <div className="flex justify-center gap-4">
                <button
                  onClick={loadExampleData}
                  className="inline-flex items-center gap-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-200 transition-colors"
                >
                  <FileText className="w-5 h-5" />
                  Ver Exemplo
                </button>
                <button
                  onClick={() => setCurrentView('new')}
                  className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  Nova Análise
                </button>
              </div>
            </div>
          ) : (
            <div className="grid gap-6">
              {analyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer"
                  onClick={() => {
                    setSelectedAnalysis(analysis);
                    setCurrentView('detail');
                  }}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-800">
                          {analysis.employeeName}
                        </h3>
                        <span className="flex items-center gap-1 text-green-600 text-sm font-medium bg-green-50 px-3 py-1 rounded-full">
                          <CheckCircle className="w-4 h-4" />
                          Concluído
                        </span>
                      </div>
                      <p className="text-gray-600">{analysis.employerName}</p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteAnalysis(analysis.id);
                      }}
                      className="text-red-500 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Créditos</p>
                      <p className="text-lg font-bold text-green-600">
                        {formatCurrency(analysis.totalCreditos)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Débitos</p>
                      <p className="text-lg font-bold text-red-600">
                        {formatCurrency(analysis.totalDebitos)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Valor Líquido</p>
                      <p className="text-lg font-bold text-blue-600">
                        {formatCurrency(analysis.valorLiquido)}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-400 mt-4">
                    Criado em {formatDate(analysis.createdAt)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Renderização do formulário de nova análise
  if (currentView === 'new') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={() => setCurrentView('list')}
            className="text-blue-600 hover:text-blue-700 mb-6 flex items-center gap-2"
          >
            ← Voltar
          </button>

          <div className="bg-white rounded-2xl shadow-lg p-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-2">Nova Análise</h2>
            <p className="text-gray-600 mb-8">
              Faça upload dos documentos para análise automática com IA
            </p>

            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Termo de Rescisão (TRCT) *
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
                  className="hidden"
                  id="termo-upload"
                />
                <label htmlFor="termo-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  {termoFile ? (
                    <p className="text-green-600 font-medium">{termoFile.name}</p>
                  ) : (
                    <>
                      <p className="text-gray-600 font-medium mb-1">
                        Clique para fazer upload
                      </p>
                      <p className="text-sm text-gray-400">PDF - Máximo 10MB</p>
                    </>
                  )}
                </label>
              </div>
            </div>

            <div className="mb-8">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Valores FGTS (Preenchimento Manual - Opcional)
              </label>
              <div className="grid grid-cols-3 gap-4 bg-blue-50 p-6 rounded-xl border border-blue-200">
                <div>
                  <label className="block text-xs text-gray-600 mb-2">Saldo FGTS (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={manualFgts.saldoFgts}
                    onChange={(e) => setManualFgts({...manualFgts, saldoFgts: e.target.value})}
                    placeholder="0,00"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-2">Multa 40% (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={manualFgts.multaFgts}
                    onChange={(e) => setManualFgts({...manualFgts, multaFgts: e.target.value})}
                    placeholder="0,00"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-2">Total FGTS (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={manualFgts.totalFgts}
                    onChange={(e) => setManualFgts({...manualFgts, totalFgts: e.target.value})}
                    placeholder="0,00"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                💡 Preencha manualmente caso o documento não contenha informações de FGTS
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setCurrentView('list')}
                className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors font-medium"
                disabled={isProcessing}
              >
                Cancelar
              </button>
              <button
                onClick={processAnalysis}
                disabled={!termoFile || isProcessing}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isProcessing ? (
                  <>
                    <Clock className="w-5 h-5 animate-spin" />
                    Processando...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Analisar Documentos
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Renderização dos detalhes da análise
  if (currentView === 'detail' && selectedAnalysis) {
    const creditos = selectedAnalysis.items.filter(item => item.tipo === 'credito');
    const debitos = selectedAnalysis.items.filter(item => item.tipo === 'debito');

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-6xl mx-auto">
          <button
            onClick={() => {
              setCurrentView('list');
              setSelectedAnalysis(null);
            }}
            className="text-blue-600 hover:text-blue-700 mb-6 flex items-center gap-2"
          >
            ← Voltar
          </button>

          <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                  {selectedAnalysis.employeeName}
                </h1>
                <p className="text-lg text-gray-600">{selectedAnalysis.employerName}</p>
              </div>
              <button
                onClick={handlePrint}
                className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors shadow-lg"
              >
                <Download className="w-5 h-5" />
                Gerar Relatório
              </button>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <div>
                <p className="text-sm text-gray-500 mb-1">Data da Rescisão</p>
                <p className="text-lg font-semibold">{formatDate(selectedAnalysis.rescissionDate)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Tipo de Rescisão</p>
                <p className="text-lg font-semibold">{selectedAnalysis.rescissionType}</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-xl">
                <p className="text-sm text-gray-600 mb-2">Total de Créditos</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(selectedAnalysis.totalCreditos)}
                </p>
                <p className="text-xs text-gray-500 mt-1">Valores a receber</p>
              </div>
              <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-xl">
                <p className="text-sm text-gray-600 mb-2">Total de Débitos</p>
                <p className="text-2xl font-bold text-red-600">
                  {formatCurrency(selectedAnalysis.totalDebitos)}
                </p>
                <p className="text-xs text-gray-500 mt-1">Descontos aplicados</p>
              </div>
              <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-xl">
                <p className="text-sm text-gray-600 mb-2">Valor Líquido</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(selectedAnalysis.valorLiquido)}
                </p>
                <p className="text-xs text-gray-500 mt-1">Valor final a receber</p>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xl font-bold text-green-600 mb-4 flex items-center gap-2">
                💰 Valores a Receber
              </h3>
              <div className="space-y-4">
                {creditos.map((item, index) => (
                  <div key={index} className="border-l-4 border-green-500 bg-green-50 p-6 rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="bg-green-600 text-white px-3 py-1 rounded-lg text-sm font-bold">
                          {item.codigo}
                        </span>
                        <h4 className="font-bold text-gray-800">{item.descricao}</h4>
                      </div>
                      <span className="text-xl font-bold text-green-600">
                        {formatCurrency(item.valor)}
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm mt-2">{item.explicacao}</p>
                  </div>
                ))}
              </div>
            </div>

            {debitos.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-bold text-red-600 mb-4 flex items-center gap-2">
                  📉 Descontos Aplicados
                </h3>
                <div className="space-y-4">
                  {debitos.map((item, index) => (
                    <div key={index} className="border-l-4 border-red-500 bg-red-50 p-6 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className="bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-bold">
                            {item.codigo}
                          </span>
                          <h4 className="font-bold text-gray-800">{item.descricao}</h4>
                        </div>
                        <span className="text-xl font-bold text-red-600">
                          {formatCurrency(item.valor)}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mt-2">{item.explicacao}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedAnalysis.observacoes.length > 0 && (
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  📋 Informações sobre a Rescisão
                </h3>
                <div className="space-y-4">
                  {selectedAnalysis.observacoes.map((obs, index) => (
                    <p key={index} className="text-gray-700 leading-relaxed">
                      {obs}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Modal de impressão */}
        {showPrintModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6">
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
                <h3 className="text-2xl font-bold text-gray-800">Relatório HTML</h3>
                <button
                  onClick={() => setShowPrintModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              <div className="p-6">
                <p className="text-gray-600 mb-4">
                  Copie o código HTML abaixo e salve como arquivo .html para gerar o PDF
                </p>
                <textarea
                  value={printHtml}
                  readOnly
                  className="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm"
                />
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={copyToClipboard}
                    className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors font-medium"
                  >
                    Copiar HTML
                  </button>
                  <button
                    onClick={() => setShowPrintModal(false)}
                    className="flex-1 border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-50 transition-colors font-medium"
                  >
                    Fechar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
}
