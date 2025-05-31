"use client"

import React, { ComponentProps } from 'react'
import { Button } from "@/components/ui/button"
import { Facebook, Linkedin, Youtube, Instagram } from 'lucide-react'
import { useState } from "react"
import { Textarea } from "@/components/ui/textarea"
import { useRouter } from 'next/navigation'

// Custom Slider Component
function PriceRangeSlider({ label }: { label: string }) {
  const [minValue, setMinValue] = useState(0)
  const [maxValue, setMaxValue] = useState(100)

  // Convert slider position (0-100) to price
  const positionToPrice = (position: number): number => {
    if (position <= 50) {
      // 0-50% maps to 0-100 yuan
      return Math.round((position / 50) * 100)
    } else if (position <= 90) {
      // 50-90% maps to 100-300 yuan
      return Math.round(100 + ((position - 50) / 40) * 200)
    } else if (position <= 99) {
      // 90-99% maps to 300-1000 yuan
      return Math.round(300 + ((position - 90) / 9) * 700)
    } else {
      // 99-100% maps to "无上限"
      return Infinity
    }
  }

  // Convert price to slider position (0-100)
  const priceToPosition = (price: number): number => {
    if (price <= 100) {
      return (price / 100) * 50
    } else if (price <= 300) {
      return 50 + ((price - 100) / 200) * 40
    } else if (price <= 1000) {
      return 90 + ((price - 300) / 700) * 9
    } else {
      return 100
    }
  }

  const formatPrice = (price: number): string => {
    if (price === Infinity) return "无上限"
    return `￥${price}`
  }

  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const position = parseInt(e.target.value)
    setMinValue(position)
  }

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const position = parseInt(e.target.value)
    setMaxValue(position)
  }

  const minPrice = positionToPrice(minValue)
  const maxPrice = positionToPrice(maxValue)

  return (
    <div className="space-y-4">
      <div>
        <label className="text-lg font-medium text-gray-800">{label}</label>
      </div>
      
      <div className="relative">
        <div className="relative h-2 bg-gray-200 rounded-full">
          <div 
            className="absolute h-2 bg-black rounded-full"
            style={{
              left: `${minValue}%`,
              width: `${maxValue - minValue}%`
            }}
          />
          <input
            type="range"
            min="0"
            max="100"
            value={minValue}
            onChange={handleMinChange}
            className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer slider-thumb"
            style={{ zIndex: 2 }}
          />
          <input
            type="range"
            min="0"
            max="100"
            value={maxValue}
            onChange={handleMaxChange}
            className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer slider-thumb"
            style={{ zIndex: 2 }}
          />
        </div>
        
        <div className="flex justify-between mt-2 text-sm text-gray-600">
          <span>{formatPrice(minPrice)}</span>
          <span>{formatPrice(maxPrice)}</span>
        </div>
      </div>

      <style jsx>{`
        .slider-thumb::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #000;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .slider-thumb::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #000;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
      `}</style>
    </div>
  )
}

// Rating Slider Component (0-5 scale with snap points)
function RatingSlider({ label, description }: { label: string; description?: string }) {
  const [value, setValue] = useState(2.5) // Default to middle position

  const snapPoints = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = parseFloat(e.target.value)
    // Find the nearest snap point
    const nearest = snapPoints.reduce((prev, curr) => 
      Math.abs(curr - rawValue) < Math.abs(prev - rawValue) ? curr : prev
    )
    setValue(nearest)
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-start">
        <div>
          <label className="text-lg font-medium text-gray-800">{label}</label>
          {description && (
            <p className="text-sm text-gray-500 mt-1">{description}</p>
          )}
        </div>
        <span className="text-sm font-medium text-gray-800">{value.toFixed(1)} 分</span>
      </div>
      
      <div className="relative">
        <div className="relative h-2 bg-gray-200 rounded-full">
          <div 
            className="absolute h-2 bg-black rounded-full"
            style={{ width: `${(value / 5) * 100}%` }}
          />
          <input
            type="range"
            min="0"
            max="5"
            step="0.1"
            value={value}
            onChange={handleChange}
            className="absolute w-full h-2 bg-transparent appearance-none cursor-pointer rating-slider"
          />
        </div>
        
        {/* Snap point indicators */}
        <div className="flex justify-between mt-2">
          {snapPoints.map((point, index) => (
            <div key={index} className="w-1 h-1 bg-gray-400 rounded-full" />
          ))}
        </div>
        
        <div className="flex justify-between mt-1 text-xs text-gray-500">
          <span>0</span>
          <span>5</span>
        </div>
      </div>

      <style jsx>{`
        .rating-slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #000;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .rating-slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #000;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
      `}</style>
    </div>
  )
}

// Custom Textarea Field Component
function TextareaField({ label, description, defaultValue = "无" }: { 
  label: string; 
  description?: string;
  defaultValue?: string;
}) {
  const [value, setValue] = useState(defaultValue)

  return (
    <div className="space-y-2">
      <div>
        <label className="text-lg font-medium text-gray-800">{label}</label>
        {description && (
          <p className="text-sm text-gray-500 mt-1">{description}</p>
        )}
      </div>
      <Textarea 
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="min-h-[100px] border-gray-300 focus:border-black focus:ring-black"
      />
    </div>
  )
}

export default function PreferencesPage() {
  const router = useRouter()
  
  return (
    <div className="flex flex-col min-h-screen">
      <header className="flex h-16 items-center border-b px-4 w-full justify-end">
        <Button 
          variant="ghost" 
          onClick={() => router.push('/chatbot')}
        >
          就餐地点推荐
        </Button>
      </header>
      <div className="flex-1 container mx-auto py-6">
        {/* Main Content */}
        <main className="px-6 py-8 max-w-6xl mx-auto">
          {/* Page Title */}
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6">个人偏好设置</h1>
          
          {/* Description */}
          <p className="text-gray-600 mb-16 max-w-4xl">
            请在下面输入您对餐厅与食物的所有偏好和需求，以下所有内容仅作为推荐算法基地点的参考依据。以下所有项均为选项，即使不填也一样可以使用我们的服务！
          </p>

          {/* Task 1: Price Range */}
          <section className="mb-16">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-8">您所期望的餐厅人均消费为多少？</h2>
            
            <div className="max-w-2xl">
              <PriceRangeSlider label="人均消费范围" />
            </div>
          </section>

          {/* Task 2: Rating Preferences */}
          <section className="mb-16">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-8">您在选择就餐地点时对以下各项的重视或敏感程度？</h2>
            
            <div className="max-w-2xl space-y-5">
              <RatingSlider label="性价比" />
              
              <RatingSlider 
                label="卫生情况" 
                description="如餐厨具卫生程度、食材新鲜程度、是否公示食品安全信息等" 
              />
              
              <RatingSlider label="用餐环境" />
              
              <RatingSlider label="餐厅距离 & 交通便利程度" />
              
              <RatingSlider label="排队等位时间 & 上菜速度" />
              
              <RatingSlider 
                label="在美食推荐平台上的综合评分高低" 
                description="如大众点评等" 
              />
              
              <RatingSlider label="餐厅服务" />
              
              <RatingSlider label="菜品口味" />
              
              <RatingSlider label="菜品健康程度" />
              
              <RatingSlider label="菜品热量 & 营养成分" />
            </div>
          </section>

          {/* Task 3: Food Preferences */}
          <section className="mb-16">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-8">您对菜品类型、口味的偏好？</h2>
            
            <div className="max-w-2xl space-y-8">
              <TextareaField 
                label="有什么是您绝对不能吃的东西？" 
                description="您可以写具体的食材，如过敏原等；您也可以在这里写您需要忌口的原因，如&quot;糖尿病&quot;等"
              />
              
              <TextareaField 
                label="您喜欢吃什么？" 
                description="您可以写菜品或食物名称，如&quot;披萨&quot;等；您也可以写具体菜系类型，如&quot;川菜&quot;等；您也可以写口味偏好，如&quot;清淡的东西&quot;等。写什么都可以！"
              />
              
              <TextareaField 
                label="您讨厌吃什么？" 
                description="您可以写菜品或食物名称，如&quot;香菜&quot;等；您也可以写具体菜系类型或者是口味偏好，如&quot;重油重盐的东西&quot;等。写什么都可以！"
              />
              
              <RatingSlider label="您对辣味的接受程度？" />
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="bg-gray-50 py-12 px-6 mt-20">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">菜根探</h3>
                <div className="flex space-x-4">
                  <Facebook className="w-5 h-5 text-gray-600 hover:text-gray-800" />
                  <Linkedin className="w-5 h-5 text-gray-600 hover:text-gray-800" />
                  <Youtube className="w-5 h-5 text-gray-600 hover:text-gray-800" />
                  <Instagram className="w-5 h-5 text-gray-600 hover:text-gray-800" />
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-4">了解菜根探</h4>
                <div className="space-y-2 text-gray-600 text-sm">
                  <div>我们为什么想做菜根探？</div>
                  <div>您的个人数据将安全吗？</div>
                  <div>我们为什么叫菜根探产品展示？</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-4">关于我们</h4>
                <div className="space-y-2 text-gray-600 text-sm">
                  <div>我们是谁？</div>
                  <div>什么是菜根探？</div>
                  <div>联系我们登录？</div>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
