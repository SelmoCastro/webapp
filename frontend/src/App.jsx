import { useState, useEffect, useMemo } from 'react'
import { supabase } from './lib/supabase'
import ProductCard from './components/ProductCard'
import HistoryModal from './components/HistoryModal'
import Filters from './components/Filters'
import { calculateTrend, isLowestPrice, categorizeProduct, isKit } from './utils/priceAnalytics'
import { LineChart } from 'lucide-react'
import './App.css'

function App() {
  const [rawData, setRawData] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProductGroup, setSelectedProductGroup] = useState(null)

  // States para Filtros
  const [selectedStores, setSelectedStores] = useState(['Kabum', 'Pichau', 'Terabyte'])
  const [selectedCategories, setSelectedCategories] = useState(['GPU', 'CPU', 'RAM', 'Motherboard', 'Storage', 'PSU', 'Outros']) // Inicia com todos marcados? Ou vazio significa todos? Vamos iniciar com todos para facilitar.

  useEffect(() => {
    fetchProducts()
  }, [])

  async function fetchProducts() {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('price_history')
        .select('*')
        .order('timestamp', { ascending: false })

      if (error) {
        console.error('Erro ao buscar produtos:', error)
      } else {
        setRawData(data || [])
      }
    } catch (e) {
      console.error('Erro inesperado:', e)
    } finally {
      setLoading(false)
    }
  }

  // Agrupar produtos duplicados (mesmo nome e loja) E Calcular Analytics
  const processedProducts = useMemo(() => {
    const groups = {}

    rawData.forEach(item => {
      // Criar chave única baseada em nome e loja
      const key = `${item.store}-${item.product_name}`

      if (!groups[key]) {
        groups[key] = {
          product: item, // Mantém o item mais recente
          history: []
        }
      }
      groups[key].history.push(item)
    })

    // Retornar array dos produtos mais recentes com campos extras
    return Object.values(groups).map(g => {
      const history = g.history;
      const currentPrice = g.product.price;

      return {
        ...g.product,
        fullHistory: history,
        trend: calculateTrend(currentPrice, history),
        isLowestPrice: isLowestPrice(currentPrice, history),
        computedCategory: categorizeProduct(g.product.product_name)
      }
    })
  }, [rawData])


  const filteredProducts = processedProducts.filter(item => {
    const matchesSearch = item.product_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStore = selectedStores.length === 0 || selectedStores.includes(item.store);
    const matchesCategory = selectedCategories.length === 0 || selectedCategories.includes(item.computedCategory);

    return matchesSearch && matchesStore && matchesCategory;
  })

  return (
    <>
      <div className="header">
        <h1>PC Price Tracker 🖥️</h1>
        <p>Monitoramento de preços Kabum, Pichau e Terabyte</p>

        <input
          type="text"
          placeholder="Buscar produto..."
          className="search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="app-container">

        <Filters
          selectedStores={selectedStores}
          setSelectedStores={setSelectedStores}
          selectedCategories={selectedCategories}
          setSelectedCategories={setSelectedCategories}
        />

        <div className="main-content">
          {loading ? (
            <p>Carregando ofertas...</p>
          ) : (
            <div className="products-grid">
              {filteredProducts.length > 0 ? (
                filteredProducts.map((product) => (
                  <div key={`${product.store}-${product.product_name}`} style={{ position: 'relative' }}>
                    <ProductCard product={product} />
                    <button
                      className="history-btn"
                      onClick={() => setSelectedProductGroup({ product, history: product.fullHistory })}
                      title="Ver Histórico"
                    >
                      <LineChart size={20} />
                    </button>
                  </div>
                ))
              ) : (
                <p>Nenhum produto encontrado.</p>
              )}
            </div>
          )}
        </div>
      </div>

      {selectedProductGroup && (
        <HistoryModal
          productGroup={selectedProductGroup}
          onClose={() => setSelectedProductGroup(null)}
        />
      )}
    </>
  )
}

export default App

