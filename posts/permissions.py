from rest_framework.permissions import BasePermission

class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        print("==== PERMISSION DEBUG ====")
        print("obj.author:", obj.author)
        print("obj.author.id:", obj.author.id)
        print("request.user:", request.user)
        print("request.user.id:", request.user.id)
        print("Admin group exists? ->", request.user.groups.filter(name="Admin").exists())
        print("IS MATCH? ->", obj.author.id == request.user.id)
        print("===========================")

        # Admin bypass
        if request.user.groups.filter(name="Admin").exists():
            print("✅ Admin passed!")
            return True

        # Author check
        if obj.author.id == request.user.id:
            print("✅ Author passed!")
            return True

        print("❌ Blocked!")
        return False
