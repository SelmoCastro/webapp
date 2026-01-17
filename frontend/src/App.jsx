import { useState, useEffect, useMemo } from 'react'
import { supabase } from './lib/supabase'
import ProductCard from './components/ProductCard'
import HistoryModal from './components/HistoryModal'
import { LineChart } from 'lucide-react'
import './App.css'

function App() {
  const [rawData, setRawData] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProductGroup, setSelectedProductGroup] = useState(null)

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

  // Agrupar produtos duplicados (mesmo nome e loja)
  const groupedProducts = useMemo(() => {
    const groups = {}

    rawData.forEach(item => {
      // Criar chave única baseada em nome e loja
      const key = `${item.store}-${item.product_name}`

      if (!groups[key]) {
        groups[key] = {
          product: item, // Mantém o item mais recente (devido ao sort do SQL ou timestamp)
          history: []
        }
      }
      groups[key].history.push(item)
    })

    // Retornar array dos produtos mais recentes
    return Object.values(groups).map(g => ({
      ...g.product,
      fullHistory: g.history
    }))
  }, [rawData])


  const filteredProducts = groupedProducts.filter(item =>
    item.product_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

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

      {loading ? (
        <p>Carregando ofertas...</p>
      ) : (
        <div className="products-grid">
          {filteredProducts.length > 0 ? (
            filteredProducts.map((product) => (
              <div key={product.id} style={{ position: 'relative' }}>
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

