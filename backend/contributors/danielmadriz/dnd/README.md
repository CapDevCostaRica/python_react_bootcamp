# Forward Proxy Caching Service - Exercise #1

## 🏗️ **Layered Architecture Solution**

This service implements a "Forward Proxy Caching" system for D&D 5e monster data using a layered architecture for escalability in following exercises.

## 📁 **Project Structure**

```
backend/contributors/danielmadriz/dnd/
├── src/                          # Source code with layered architecture
│   ├── domain/                   # Domain Layer - Business entities & interfaces
│   │   ├── entities/             # Domain entities package
│   │   │   ├── __init__.py       # Exports all entities
│   │   │   ├── monster.py        # Monster entity
│   │   │   ├── monster_list.py   # MonsterList entity
│   │   │   └── cache_result.py   # CacheResult entity
│   │   └── interfaces.py         # Abstract contracts for Dependency Injection
│   ├── application/              # Application Layer - Business logic
│   ├── infrastructure/           # Infrastructure Layer - External concerns
│   ├── presentation/             # Presentation Layer - Web API
│   └── crosscutting/             # Crosscutting Concerns
├── tests/                        # Comprehensive test suite
├── main.py                       # Application entry point
├── requirements.txt              # Dependencies
├── pytest.ini                    # Test configuration
└── README.md
```

## **Entity Organization Strategy**

We follow the separate Files Approach for organizing domain entities, even though this exercise only uses a small set of interfaces it will growth across multiple weeks and the idea is to have a better separation of concerns that escales with the application:

#### **1. Separate Files Approach (Current Implementation)**

```
src/domain/entities/
├── __init__.py       # Package initialization & exports
├── monster.py
├── monster_list.py
└── cache_result.py

```

#### **2. ABC Interface Definition Approach**

For our interface definition we favored the Abstract Base Class (ABC) over Protocol since it provides the following benefits:

- Contract Enforcesment
- Runtime validation
- Clear intent
  With might be important for scalability pourposes

## 📝 **License**

This project is part of the Python React Bootcamp Exercise #1.
