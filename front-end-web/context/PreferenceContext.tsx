"use client"

import { createContext, useContext, useState, ReactNode } from 'react';

// 定义数据结构
interface PreferenceData {
  priceRange: {
    min: number;
    max: number;
  };
  ratings: {
    valueForMoney: number;
    hygiene: number;
    environment: number;
    distance: number;
    waitTime: number;
    platformRating: number;
    service: number;
    taste: number;
    health: number;
    nutrition: number;
    spiciness: number;
  };
  preferences: {
    allergies: string;
    likes: string;
    dislikes: string;
  };
}

// 创建初始数据
const initialPreferences: PreferenceData = {
  priceRange: {
    min: 0,
    max: 100,
  },
  ratings: {
    valueForMoney: 2.5,
    hygiene: 2.5,
    environment: 2.5,
    distance: 2.5,
    waitTime: 2.5,
    platformRating: 2.5,
    service: 2.5,
    taste: 2.5,
    health: 2.5,
    nutrition: 2.5,
    spiciness: 2.5,
  },
  preferences: {
    allergies: "无",
    likes: "无",
    dislikes: "无",
  },
};

// 这个interface就相当于是Typescript（带有变量类型定义的javasript语言）的“结构体”struct。
// 运行程序时会将Typescript编译成Javascript，所以这个接口与外部程序调用等完全无关，只是为了在代码中更好地定义数据结构和类型检查。
interface PreferenceContextType {
  preferences: PreferenceData;
  updatePriceRange: (min: number, max: number) => void;
  updateRating: (key: keyof PreferenceData['ratings'], value: number) => void;
  updatePreference: (key: keyof PreferenceData['preferences'], value: string) => void;
  savePreferences: () => void;
}

// 创建一个全局状态容器，用于在不同组件之间共享数据。
// 其格式为上面定义的interface（包括PreferenceData数据和四个函数）或者undifined。
const PreferenceContext = createContext<PreferenceContextType | undefined>(undefined);

// 定义一个叫PreferenceProvider的函数（React组件），这样其他程序可以import来用PreferenceProvider这个函数（React组件）。
// 在前端调用的这个函数（React组件）时候要用<PreferenceProvider> 传入的参数 </PreferenceProvider>格式，或<PreferenceProvider/>调用。
// React组件在定义时，括号里的东西叫props，props里可以包含一些参数，这些参数可以在组件的render函数中使用。
export function PreferenceProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] = useState<PreferenceData>(initialPreferences);

  const updatePriceRange = (min: number, max: number) => {
    setPreferences(prev => ({
      ...prev,
      priceRange: { min, max }
    }));
  };

  const updateRating = (key: keyof PreferenceData['ratings'], value: number) => {
    setPreferences(prev => ({
      ...prev,
      ratings: {
        ...prev.ratings,
        [key]: value
      }
    }));
  };

  const updatePreference = (key: keyof PreferenceData['preferences'], value: string) => {
    setPreferences(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: value
      }
    }));
  };

  const savePreferences = () => {
    // 将数据转换为 JSON 并保存到 localStorage
    const jsonData = JSON.stringify(preferences);
    localStorage.setItem('userPreferences', jsonData);
    console.log('已保存的偏好设置：', jsonData);
    // 这里可以添加保存成功的提示
    alert('设置已暂存！');
  };

  return (
    <PreferenceContext.Provider 
      value={{ 
        preferences, 
        updatePriceRange, 
        updateRating, 
        updatePreference,
        savePreferences 
      }}
    >
      {children}
    </PreferenceContext.Provider>
  );
}

export function usePreferences() {
  const context = useContext(PreferenceContext);
  if (context === undefined) {
    throw new Error('usePreferences must be used within a PreferenceProvider');
  }
  return context;
}

export type { PreferenceData };