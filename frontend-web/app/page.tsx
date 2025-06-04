import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Facebook, Linkedin, Youtube, Instagram } from 'lucide-react'
import Image from "next/image"
import Link from "next/link"

export default function Component() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4">
        <div className="text-xl font-semibold text-gray-800">菜根探</div>
        <nav className="hidden md:flex items-center space-x-8">
          <a href="#" className="text-gray-600 hover:text-gray-800">
            关于我们
          </a>
          <a href="#" className="text-gray-600 hover:text-gray-800">
            了解菜根探
          </a>
          <a href="#" className="text-gray-600 hover:text-gray-800">
            欢迎帮助
          </a>
          <Link href="/preferences">
            <Button className="bg-black text-white hover:bg-gray-800 px-6">登录</Button>
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative h-[400px] bg-cover bg-center" style={{ backgroundImage: "url('/new-hero-bg.png')" }}>
        <div className="absolute inset-0 bg-black/30" style={{ backdropFilter: "blur(1px)" }} />
        <div className="relative z-10 flex flex-col justify-center h-full px-6 max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">菜根探</h1>
          <p className="text-lg text-white mb-8 max-w-md">专为你私人定制，值得喜爱的智能美食推荐助手</p>
          <Button className="bg-white text-black hover:bg-gray-100 w-fit px-8 py-3">即刻体验</Button>
        </div>
      </section>

      {/* Scenarios Section */}
      <section className="py-16 px-6 max-w-6xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-12">你是否为以下场合感到发愁？</h2>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Scenario 1 */}
          <Card className="overflow-hidden">
            <Image
              src="/scenario-travel.png"
              alt="外出旅游"
              width={300}
              height={200}
              className="w-full h-48 object-cover"
            />
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-3">外出旅游</h3>
              <p className="text-gray-600 text-sm">想试试当地特色传统美食，可面对人满为患的众多网红店不知所措？</p>
            </CardContent>
          </Card>

          {/* Scenario 2 */}
          <Card className="overflow-hidden">
            <Image
              src="/scenario-friends.png"
              alt="朋友小聚"
              width={300}
              height={200}
              className="w-full h-48 object-cover"
            />
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-3">朋友小聚</h3>
              <p className="text-gray-600 text-sm">大家临时需要决定吃什么，可大家又都拿不定主意，在路边纠结？</p>
            </CardContent>
          </Card>

          {/* Scenario 3 */}
          <Card className="overflow-hidden">
            <Image
              src="/scenario-dating.png"
              alt="情侣约会"
              width={300}
              height={200}
              className="w-full h-48 object-cover"
            />
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-3">情侣约会</h3>
              <p className="text-gray-600 text-sm">想要精心挑选有意境地点，给TA一个深刻的印象，却拿不定主意？</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 px-6 max-w-6xl mx-auto">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-8">不妨试试菜根探！</h2>

        <div className="space-y-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">真正懂你的智能美食推荐助手</h3>
            <p className="text-gray-600">
              在个人设置中输入您对就餐与食物的所有偏好和需求，我们将只为您推荐符合您喜好食习惯的餐厅。
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">能对话可交流的智能美食推荐助手</h3>
            <p className="text-gray-600">
              在询问推荐就餐地点时，随心所欲地输入您的想法，您可以和智能推荐官实交流对话。
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">无广告营销的智能美食推荐助手</h3>
            <p className="text-gray-600">所有推荐由专属智能算法生成，去除广告与软文，为您推荐真正的宝藏餐厅。</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 mt-12">
          <Button className="bg-black text-white hover:bg-gray-800 px-8 py-3">即刻体验</Button>
          <Button variant="outline" className="px-8 py-3">
            登录/注册
          </Button>
        </div>
      </section>

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
  )
}
