"""
实时协作模块测试
"""
import pytest
import time

from src.services.collaboration import (
    RealTimeCollaboration,
    CollaborationProject,
    Collaborator,
    CollaboratorRole,
    ProjectStatus,
    CollaborationSession
)


class TestRealTimeCollaboration:
    """测试实时协作系统"""
    
    @pytest.fixture
    def collab(self):
        return RealTimeCollaboration()
    
    def test_create_project(self, collab):
        """测试创建项目"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="test@example.com",
            description="这是一个测试项目"
        )
        
        assert isinstance(project, CollaborationProject)
        assert project.name == "测试项目"
        assert project.owner_id
        assert len(project.collaborators) == 1
        assert project.status == ProjectStatus.DRAFT
        assert len(project.activities) == 1
    
    def test_invite_collaborator(self, collab):
        """测试邀请协作者"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        collaborator = collab.invite_collaborator(
            project_id=project.id,
            username="协作者",
            email="collaborator@example.com",
            role=CollaboratorRole.EDITOR
        )
        
        assert isinstance(collaborator, Collaborator)
        assert collaborator.username == "协作者"
        assert collaborator.role == CollaboratorRole.EDITOR
        assert len(project.collaborators) == 2
    
    def test_invite_collaborator_duplicate(self, collab):
        """测试重复邀请协作者"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        # 第一次邀请
        collab.invite_collaborator(
            project_id=project.id,
            username="协作者",
            email="collaborator@example.com"
        )
        
        # 重复邀请
        result = collab.invite_collaborator(
            project_id=project.id,
            username="协作者2",
            email="collaborator@example.com"
        )
        
        assert result is None
    
    def test_remove_collaborator(self, collab):
        """测试移除协作者"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        collaborator = collab.invite_collaborator(
            project_id=project.id,
            username="协作者",
            email="collaborator@example.com"
        )
        
        result = collab.remove_collaborator(
            project_id=project.id,
            collaborator_id=collaborator.id
        )
        
        assert result is True
        assert len(project.collaborators) == 1
    
    def test_remove_owner(self, collab):
        """测试移除所有者（应该失败）"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        result = collab.remove_collaborator(
            project_id=project.id,
            collaborator_id=project.owner_id
        )
        
        assert result is False
    
    def test_update_project_data(self, collab):
        """测试更新项目数据"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        result = collab.update_project_data(
            project_id=project.id,
            collaborator_id=project.owner_id,
            data={"bpm": 120, "key": "C"}
        )
        
        assert result is True
        assert project.song_data["bpm"] == 120
        assert project.song_data["key"] == "C"
    
    def test_update_project_data_no_permission(self, collab):
        """测试无权限更新"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        viewer = collab.invite_collaborator(
            project_id=project.id,
            username="查看者",
            email="viewer@example.com",
            role=CollaboratorRole.VIEWER
        )
        
        result = collab.update_project_data(
            project_id=project.id,
            collaborator_id=viewer.id,
            data={"bpm": 120}
        )
        
        assert result is False
    
    def test_add_comment(self, collab):
        """测试添加评论"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        activity = collab.add_comment(
            project_id=project.id,
            collaborator_id=project.owner_id,
            comment="这首歌很棒！",
            position={"time": 30.0}
        )
        
        assert activity is not None
        assert activity.action == "添加评论"
        assert "这首歌很棒！" in activity.description
    
    def test_get_project_history(self, collab):
        """测试获取项目历史"""
        project = collab.create_project(
            name="测试项目",
            owner_username="测试用户",
            owner_email="owner@example.com"
        )
        
        history = collab.get_project_history(project.id, limit=10)
        
        assert isinstance(history, list)
        assert len(history) > 0


class TestCollaborationSession:
    """测试协作会话"""
    
    @pytest.fixture
    def session(self):
        collab = RealTimeCollaboration()
        return CollaborationSession(collab)
    
    def test_join_project(self, session):
        """测试加入项目"""
        project = session.collaboration.create_project(
            name="测试项目",
            owner_username="所有者",
            owner_email="owner@example.com"
        )
        
        result = session.join_project(
            project_id=project.id,
            username="协作者",
            email="collaborator@example.com"
        )
        
        assert result is True
        assert session.project_id == project.id
        assert session.collaborator_id is not None
    
    def test_leave_project(self, session):
        """测试离开项目"""
        project = session.collaboration.create_project(
            name="测试项目",
            owner_username="所有者",
            owner_email="owner@example.com"
        )
        
        session.join_project(
            project_id=project.id,
            username="协作者",
            email="collaborator@example.com"
        )
        
        session.leave_project()
        
        assert session.project_id is None
        assert session.collaborator_id is None
    
    def test_update_data(self, session):
        """测试更新数据"""
        project = session.collaboration.create_project(
            name="测试项目",
            owner_username="所有者",
            owner_email="owner@example.com"
        )
        
        session.join_project(
            project_id=project.id,
            username="协作者",
            email="collaborator@example.com"
        )
        
        result = session.update_data({"bpm": 120})
        
        assert result is True
